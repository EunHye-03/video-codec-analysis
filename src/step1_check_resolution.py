import os
import pandas as pd
import config as cfg


def run_check_resolution(data_path):
    # 1. 파일 목록 가져오기
    files = [f for f in os.listdir(data_path) if f.endswith(".yuv")]

    # 2. 기초 DataFrame 생성
    df = pd.DataFrame({"file_name": files})
    df = df.sort_values(by="file_name")

    # 확장자를 제외한 '기본 이름' 열 생성 (매핑용 키)
    df["base_name"] = df["file_name"].str.replace(".yuv", "", regex=False)

    # 3. 벡터화 매핑 (map 함수 활용)
    df["res_tuple"] = df["base_name"].map(cfg.RESOLUTIONS)
    df["fr_tuple"] = df["base_name"].map(cfg.FR_DICT)

    # 4. 튜플 쪼개기 (벡터화)
    df[["width", "height"]] = pd.DataFrame(df["res_tuple"].tolist(), index=df.index)
    df[["random_access", "fps", "frame_count", "start_frame"]] = pd.DataFrame(
        df["fr_tuple"].tolist(), index=df.index
    )

    # 5. 계산 연산 (벡터화)
    # 이론적 파일 크기: W * H * format_factor * Frames (config.FORMATS)
    chroma_format, format_factor = next(iter(cfg.FORMATS.items()))
    df["expected_size"] = df["width"] * df["height"] * format_factor * df["frame_count"]

    # 실제 파일 크기와 비교 (상태 확인)
    df["actual_size"] = df["file_name"].apply(
        lambda x: os.path.getsize(os.path.join(data_path, x))
    )
    df["is_valid"] = df["expected_size"] == df["actual_size"]

    # meta_df: chroma_format, format_factor는 config.FORMATS에서 가져옴 (위에서 이미 계산됨)
    df["chroma_format"] = chroma_format
    df["format_factor"] = format_factor

    # unit_size: 프레임당 바이트 (W * H * format_factor)
    df["unit_size"] = df["width"] * df["height"] * df["format_factor"]
    df["total_size"] = df["actual_size"]
    meta_df = df[
        [
            "file_name",
            "base_name",
            "width",
            "height",
            "chroma_format",
            "format_factor",
            "fps",
            "frame_count",
            "unit_size",
            "total_size",
            "is_valid",
        ]
    ].copy()

    print("✅ 매핑 및 계산 완료")

    OUTPUT_DIR = cfg.OUTPUT_REPORT_DIR
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📂 결과 폴더 생성 완료: {OUTPUT_DIR}")

    meta_df.to_csv(os.path.join(OUTPUT_DIR, "metadata_vcm.csv"), index=False)
    print("✅ 1단계 완료: metadata_vcm.csv 생성됨")

    return meta_df


if __name__ == "__main__":
    run_check_resolution(cfg.ROI_PATH)
