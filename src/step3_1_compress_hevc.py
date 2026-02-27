import os
import subprocess
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

import config as cfg


def _compress_single(args):
    """단일 파일 HEVC 압축 (멀티프로세싱 워커용)"""
    row_dict, input_root, output_root, qp = args
    file_name = row_dict["file_name"]
    base_name = row_dict["base_name"]
    w, h = int(row_dict["width"]), int(row_dict["height"])
    priority = row_dict["compress_priority"]

    input_path = os.path.join(input_root, file_name)
    output_dir = os.path.join(
        output_root, f"qp{qp}"
    )  # output_root = OUTPUT_COMPRESSED_HEVC_DIR
    output_path = os.path.join(output_dir, f"{base_name}_qp{qp}.mp4")

    if not os.path.exists(input_path):
        return priority, base_name, qp, False, f"입력 파일 없음: {input_path}"

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "yuv420p",
        "-s",
        f"{w}x{h}",
        "-i",
        input_path,
        "-c:v",
        "libx265",
        "-x265-params",
        f"random-access=1:qp={qp}",
        "-pix_fmt",
        "yuv420p",
        "-threads",
        "1",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return priority, base_name, qp, True, None
    except subprocess.CalledProcessError as e:
        return priority, base_name, qp, False, str(e.stderr) if e.stderr else str(e)


def compress_vcm_hevc_ffmpeg(input_root, output_root, qp, job_df, max_workers=None):
    """metadata_vcm + vcm_analysis_report 기반 HEVC 압축 (ProcessPoolExecutor 병렬화)"""
    if max_workers is None:
        max_workers = max(1, os.cpu_count() - 1)

    rows = job_df.to_dict("records")
    tasks = [(r, input_root, output_root, qp) for r in rows]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_compress_single, t): t for t in tasks}
        for future in as_completed(futures):
            priority, base_name, qp_val, ok, err_msg = future.result()
            if ok:
                print(f"✅ [{priority}] {base_name} 압축 완료 (QP {qp_val})")
            else:
                print(f"❌ [{priority}] {base_name} 압축 실패 (QP {qp_val}): {err_msg}")


def build_job_df(metadata_path=None, analysis_path=None):
    """metadata_vcm + vcm_analysis_report를 병합하고 compress_priority 순 정렬"""
    if metadata_path is None:
        metadata_path = os.path.join(cfg.OUTPUT_METADATA_DIR, "metadata_vcm.csv")
    if analysis_path is None:
        analysis_path = os.path.join(cfg.OUTPUT_ANALYSIS_DIR, "vcm_analysis_report.csv")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"metadata_vcm.csv 없음. step1을 먼저 실행: {metadata_path}"
        )
    if not os.path.exists(analysis_path):
        raise FileNotFoundError(
            f"vcm_analysis_report.csv 없음. step2를 먼저 실행: {analysis_path}"
        )

    meta_df = pd.read_csv(metadata_path)
    meta_df = meta_df[meta_df["is_valid"].isin([True, "True", "TRUE", 1])].copy()

    analysis_df = pd.read_csv(analysis_path)
    analysis_df = analysis_df[["file_name", "compress_priority"]].copy()

    job_df = meta_df.merge(analysis_df, on="file_name", how="inner")
    job_df = job_df.sort_values(by="compress_priority", ascending=True).reset_index(
        drop=True
    )
    os.makedirs(cfg.OUTPUT_REPORT_DIR, exist_ok=True)
    job_csv_path = os.path.join(cfg.OUTPUT_REPORT_DIR, "job_df.csv")
    job_df.to_csv(job_csv_path, index=False)
    print(f"✅ job_df.csv 생성됨: {job_csv_path}")
    return job_df


def run_compress_hevc():
    input_root = cfg.ROI_PATH
    output_root = cfg.OUTPUT_COMPRESSED_HEVC_DIR

    job_df = build_job_df()
    n_workers = max(1, os.cpu_count() - 1)
    print(f"📊 압축 대상 {len(job_df)}개 (compress_priority 순, {n_workers} 워커 병렬)")

    qp_list = cfg.QP_LIST
    for qp in qp_list:
        qp_dir = os.path.join(output_root, f"qp{qp}")
        if not os.path.exists(qp_dir):
            os.makedirs(qp_dir, exist_ok=True)
        print(f"\n🚀 QP {qp} 압축 시작...")
        compress_vcm_hevc_ffmpeg(
            input_root, output_root, qp, job_df, max_workers=n_workers
        )

    # 모든 압축이 끝난 후 ZIP 파일 생성
    import shutil

    zip_base_name = os.path.join(os.path.dirname(output_root), "compress_hevc")
    print(f"\n📦 압축 결과 ZIP 파일 생성 중: {zip_base_name}.zip")
    shutil.make_archive(zip_base_name, "zip", output_root)
    print("✅ ZIP 파일 생성 완료")


if __name__ == "__main__":
    run_compress_hevc()
