import os
import numpy as np
import cv2
import pandas as pd
import config as cfg


def run_analyze_metrics(data_path, metadata_path=None):
    """metadata_vcm.csv를 이용해 메트릭 분석 (step1 결과 활용)"""
    if metadata_path is None:
        metadata_path = os.path.join(cfg.OUTPUT_METADATA_DIR, "metadata_vcm.csv")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"metadata_vcm.csv가 없습니다. step1을 먼저 실행하세요: {metadata_path}"
        )

    meta_df = pd.read_csv(metadata_path)
    meta_df = meta_df[meta_df["is_valid"].isin([True, "True", "TRUE", 1])].copy()

    if len(meta_df) == 0:
        print("⚠️ metadata에 유효한 파일이 없습니다.")
        return pd.DataFrame()

    print(f"📊 총 {len(meta_df)}개 파일 분석을 시작합니다... (metadata_vcm 기반)")

    # Y 채널 메트릭 계산 (파일 I/O - 매 파일별 처리)
    metrics_list = [
        _compute_file_metrics(
            os.path.join(data_path, row.file_name),
            int(row.width),
            int(row.height),
            float(row.format_factor),
        )
        for row in meta_df.itertuples(index=False)
    ]

    meta_df["pixel_mean"] = [m[0] for m in metrics_list]
    meta_df["edge_density(%)"] = [m[1] for m in metrics_list]
    meta_df["temporal_diff"] = [m[2] for m in metrics_list]

    # 결과 정리 (기존 리포트 형식 유지 + metadata 컬럼 추가)
    report = meta_df[
        [
            "file_name",
            "base_name",
            "width",
            "height",
            "chroma_format",
            "format_factor",
            "frame_count",
            "pixel_mean",
            "edge_density(%)",
            "temporal_diff",
        ]
    ].copy()
    report["resolution"] = (
        report["width"].astype(int).astype(str)
        + "x"
        + report["height"].astype(int).astype(str)
    )
    report = report[
        [
            "file_name",
            "base_name",
            "resolution",
            "chroma_format",
            "format_factor",
            "frame_count",
            "pixel_mean",
            "edge_density(%)",
            "temporal_diff",
        ]
    ]
    report["pixel_mean"] = report["pixel_mean"].round(2)
    report["edge_density(%)"] = report["edge_density(%)"].round(4)
    report["temporal_diff"] = report["temporal_diff"].round(4)

    norm_edge = _min_max_norm(report["edge_density(%)"])
    norm_temporal = _min_max_norm(report["temporal_diff"])
    norm_mean = _min_max_norm(report["pixel_mean"])
    report["complexity_score"] = (
        0.4 * norm_edge + 0.5 * norm_temporal + 0.1 * norm_mean
    ).round(4)

    # 압축 우선순위: 복잡도 높은 순 (높을수록 먼저 압축)
    report = report.sort_values(by="complexity_score", ascending=False).reset_index(
        drop=True
    )
    report["compress_priority"] = range(1, len(report) + 1)

    print("✅ 메트릭 및 복잡도 점수 계산 완료")

    OUTPUT_DIR = cfg.OUTPUT_REPORT_DIR
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📂 결과 폴더 생성 완료: {OUTPUT_DIR}")

    report.to_csv(os.path.join(OUTPUT_DIR, "vcm_analysis_report.csv"), index=False)
    print("✅ 2단계 완료: vcm_analysis_report.csv 생성됨")
    print(report.head(10))
    return report


def _compute_file_metrics(path, w, h, format_factor):
    """단일 파일 Y 채널 메트릭 계산 (벡터화된 NumPy 연산 사용)"""
    frame_y_bytes = w * h
    chroma_skip = int(frame_y_bytes * (format_factor - 1))

    with open(path, "rb") as f:
        y1_raw = f.read(frame_y_bytes)
        y1 = np.frombuffer(y1_raw, dtype=np.uint8).reshape((h, w))

        f.seek(chroma_skip, 1)
        y2_raw = f.read(frame_y_bytes)

    pixel_mean = np.mean(y1)

    temporal_diff = 0.0
    if len(y2_raw) == frame_y_bytes:
        y2 = np.frombuffer(y2_raw, dtype=np.uint8).reshape((h, w))
        temporal_diff = np.float64(np.mean(cv2.absdiff(y1, y2)))

    edges = cv2.Canny(y1, 100, 200)
    edge_density = np.float64(np.sum(edges > 0)) / (w * h) * 100

    return pixel_mean, edge_density, temporal_diff


# 복잡도 점수(Complexity Score): edge_density, temporal_diff, pixel_mean 기반
# Min-max 정규화 후 가중 합 (공간/시간 복잡도 위주)
def _min_max_norm(s: pd.Series) -> pd.Series:
    lo, hi = s.min(), s.max()
    return (s - lo) / (hi - lo) if hi > lo else pd.Series(0.5, index=s.index)


if __name__ == "__main__":
    DATA_DIR = cfg.ROI_PATH
    run_analyze_metrics(DATA_DIR)
