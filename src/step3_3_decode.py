import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product

import config as cfg


def _decode_single(args):
    """단일 파일 복원 (멀티프로세싱 워커용)"""
    video_id, qp, tool, compressed_tool_dir, decode_tool_dir = args

    # 출력 폴더 생성 (워커 내에서 수행해도 되지만, 미리 만들어두는 게 안전함. 여기선 각자 확인)
    qp_folder = os.path.join(decode_tool_dir, f"qp{qp}")
    os.makedirs(qp_folder, exist_ok=True)

    final_output_path = os.path.join(qp_folder, f"{video_id}_qp{qp}.yuv")

    # 해상도 정보 가져오기 (HEVC crop용)
    if video_id not in cfg.RESOLUTIONS:
        return tool, qp, video_id, False, f"해상도 정보 없음: {video_id}"

    # step3-1, step3-2 등에서 cfg.RESOLUTIONS (4배 확대)를 사용하므로
    # 복원 시에도 동일한 해상도 기준을 따름.
    width, height = cfg.RESOLUTIONS[video_id]

    cmd = ""
    input_file = ""

    # compressed file: qpXX/video_qpXX.mp4 (HEVC, VVC 공통)
    input_file = os.path.join(
        compressed_tool_dir, f"qp{qp}", f"{video_id}_qp{qp}.mp4"
    )

    if tool == "HEVC":
        # ffmpeg crop 옵션: width:height:0:0
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-vf",
            f"crop={width}:{height}:0:0",
            "-pix_fmt",
            "yuv420p",
            final_output_path,
        ]
    else:
        # VVC 복원
        cmd = [cfg.VVC_DECODER_APP_PATH, "-b", input_file, "-o", final_output_path]

    if not os.path.exists(input_file):
        return tool, qp, video_id, False, f"파일 없음: {input_file}"

    try:
        # subprocess.run에 리스트 전달
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return tool, qp, video_id, True, None
    except subprocess.CalledProcessError as e:
        err_msg = str(e.stderr) if e.stderr else str(e)
        return tool, qp, video_id, False, err_msg


def run_decode(max_workers=None):
    if max_workers is None:
        max_workers = max(1, os.cpu_count() - 1)

    decode_base_dir = cfg.OUTPUT_DECODED_DIR
    qp_list = cfg.QP_LIST

    # 대상 영상 리스트 (FR_DICT 키 기준)
    video_keys = list(cfg.FR_DICT.keys())

    tasks = []

    print(f"🚀 복원 시작 (워커: {max_workers})")

    for tool in ["HEVC", "VVC"]:
        decode_tool_dir = os.path.join(decode_base_dir, tool)
        compressed_tool_dir = (
            cfg.OUTPUT_COMPRESSED_HEVC_DIR
            if tool == "HEVC"
            else cfg.OUTPUT_COMPRESSED_VVC_DIR
        )

        # 출력 디렉토리 미리 생성
        for qp in qp_list:
            os.makedirs(os.path.join(decode_tool_dir, f"qp{qp}"), exist_ok=True)

        batch_tasks = [
            (video_id, qp, tool, compressed_tool_dir, decode_tool_dir)
            for video_id, qp in product(video_keys, qp_list)
        ]
        tasks.extend(batch_tasks)

    # 결과 확인
    print(f"총 작업 개수: {len(tasks)}")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_decode_single, t): t for t in tasks}
        for future in as_completed(futures):
            tool, qp, video_id, ok, err_msg = future.result()
            if ok:
                print(f"✅ [{tool}] QP {qp} 복원 완료: {video_id}")
            else:
                print(f"❌ [{tool}] QP {qp} 복원 실패 ({video_id}): {err_msg}")


if __name__ == "__main__":
    run_decode()
