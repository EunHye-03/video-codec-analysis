import os
import numpy as np
import config as cfg
import pandas as pd
from skimage.metrics import peak_signal_noise_ratio as psnr_metric
from skimage.metrics import structural_similarity as ssim_metric


def run_evaluate():
    os.makedirs(cfg.OUTPUT_REPORT_DIR, exist_ok=True)

    for tool in ["HEVC", "VVC"]:
        all_results = []  # 툴별로 리스트 초기화
        print(f"🚀 {tool} 성능 평가 시작...")

        compressed_tool_dir = os.path.join(cfg.OUTPUT_COMPRESSED_DIR, tool)
        decoded_tool_dir = os.path.join(cfg.OUTPUT_DECODED_DIR, tool)

        for qp in cfg.QP_LIST:
            for file_base in cfg.FR_DICT.keys():
                width, height = cfg.RAW_RESOLUTIONS[file_base]
                fps, frame_count = cfg.FR_DICT[file_base][1], cfg.FR_DICT[file_base][2]

                # 1. 경로 설정 (파일명 규칙 주의)
                original_yuv_path = os.path.join(cfg.ROI_PATH, f"{file_base}.yuv")
                reconstructed_yuv_path = os.path.join(
                    decoded_tool_dir, f"qp{qp}", f"{file_base}_qp{qp}.yuv"
                )

                # 비트레이트 계산을 위한 압축 파일(.bin) 경로 - VVC/HEVC 동일하게 처리
                compressed_file_path = os.path.join(
                    compressed_tool_dir, f"qp{qp}", f"{file_base}_qp{qp}.bin"
                )

                if os.path.exists(reconstructed_yuv_path) and os.path.exists(
                    compressed_file_path
                ):
                    # 화질 지표 계산
                    psnr, ssim, ssnr = calculate_metrics(
                        original_yuv_path,
                        reconstructed_yuv_path,
                        width,
                        height,
                        frame_count,
                    )

                    # 비트레이트 계산
                    file_size = os.path.getsize(compressed_file_path)
                    bitrate, bpp = _calculate_bit_metrics(
                        file_size, width, height, frame_count, fps
                    )

                    if psnr is not None:
                        all_results.append(
                            {
                                "file": file_base,
                                "qp": qp,
                                "psnr": psnr,
                                "ssim": ssim,
                                "ssnr": ssnr,
                                "bitrate_kbps": bitrate,
                                "bpp": bpp,
                            }
                        )
                        print(
                            f"✅ {file_base} (QP{qp}): PSNR {psnr:.2f}, SSNR {ssnr:.2f}, Bitrate {bitrate:.2f}"
                        )
                    else:
                        print(f"⚠️ 에러 발생: {file_base} QP {qp}")
                else:
                    print(f"⚠️ 파일 없음: {file_base} QP {qp}")

        # CSV 저장 (vcm/results/report/)
        if all_results:
            df = pd.DataFrame(all_results)
            csv_path = os.path.join(cfg.OUTPUT_REPORT_DIR, f"evaluation_{tool}.csv")
            df.to_csv(csv_path, index=False)
            print(f"💾 {tool} 결과 저장 완료: {csv_path}")
        else:
            print(f"⚠️ {tool} 결과 없음: 저장 생략")


"""
def calculate_metrics(original_yuv_path, reconstructed_yuv_path, width, height, frame_count):
    if not os.path.exists(original_yuv_path) or not os.path.exists(reconstructed_yuv_path):
        return None, None, None

    psnr_values = []
    ssim_values = []
    ssnr_values = []

    with open(original_yuv_path, 'rb') as orig_file, open(reconstructed_yuv_path, 'rb') as recon_file:
        for f in range(frame_count):
            orig_y = _read_yuv_frame(orig_file, width, height)
            recon_y = _read_yuv_frame(recon_file, width, height)

            if orig_y is None or recon_y is None:
                break

            if f == 0: # 첫 프레임만 확인
                diff_check = np.sum(orig_y.astype(np.float64) - recon_y.astype(np.float64))
                print(f"DEBUG: Frame 0 Difference Sum = {diff_check}")

            psnr_y = psnr_metric(orig_y, recon_y, data_range=255)
            ssim_y = ssim_metric(orig_y, recon_y, data_range=255)
            ssnr_y = calculate_ssnr(orig_y, recon_y)

            if np.isinf(psnr_y):
                # inf가 뜨면 강제로 MSE를 찍어봅니다.
                mse = np.mean((orig_y.astype(np.float64) - recon_y.astype(np.float64)) ** 2)
                print(f"⚠️ Frame {f} is INF! MSE was: {mse}")

            psnr_values.append(psnr_y)
            ssim_values.append(ssim_y)
            ssnr_values.append(ssnr_y)

    if not psnr_values:
        return 0, 0, 0

    return np.mean(psnr_values), np.mean(ssim_values), np.mean(ssnr_values)
"""


def calculate_metrics(original_path, reconstructed_path, width, height, frame_count):
    y_size = width * height
    uv_size = (width // 2) * (height // 2)
    frame_size_bytes = y_size + 2 * uv_size

    """
    # 1. 파일 전체를 메모리에 로드 (Y 채널만 3D 배열로 변환)
    def get_y_frames(path):
        raw_data = np.fromfile(path, dtype=np.uint8)
        # 각 프레임의 시작 위치 인덱스 계산
        starts = np.arange(frame_count) * frame_size_bytes
        # 모든 프레임의 Y 영역만 추출하여 (N, H, W) 형태로 reshape
        y_frames = np.array([raw_data[s : s + y_size].reshape(height, width) for s in starts])
        return y_frames.astype(np.float64)
    """

    orig_video = _get_y_frames(
        frame_count, y_size, frame_size_bytes, width, height, original_path
    )  # Shape: (Frame, Height, Width)
    recon_video = _get_y_frames(
        frame_count, y_size, frame_size_bytes, width, height, reconstructed_path
    )  # Shape: (Frame, Height, Width)

    # 2. PSNR 벡터화 계산
    # MSE를 (N, H, W)에서 H, W 축에 대해 평균내어 프레임별 MSE 산출
    mse_per_frame = np.mean((orig_video - recon_video) ** 2, axis=(1, 2))

    # 요걸 추가해야 에러가 안 날 거예요!
    ssim_values = [
        ssim_metric(orig_video[i], recon_video[i], data_range=255)
        for i in range(frame_count)
    ]

    # MSE가 0인 경우(완전 일치) inf 방지를 위해 아주 작은 값 더하거나 처리
    psnr_values = 10 * np.log10(
        255**2 / np.where(mse_per_frame == 0, 1e-10, mse_per_frame)
    )

    # 3. SSNR 벡터화 (기존에 만든 함수를 3D 입력을 받게 조금만 수정)
    # 아래 2번 항목에서 설명하는 '배치 처리' 방식으로 SSNR을 호출하면 빠릅니다.
    ssnr_values = [
        calculate_ssnr(orig_video[i], recon_video[i]) for i in range(frame_count)
    ]

    return np.mean(psnr_values), np.mean(ssim_values), np.mean(ssnr_values)


'''
def calculate_ssnr(orig_y, recon_y, block_size=16):
    """
    Y 채널 프레임을 block_size x block_size 세그먼트로 나누어 SSNR 계산
    """
    h, w = orig_y.shape
    snr_values = []

    # 정밀한 계산을 위해 float64 변환
    orig = orig_y.astype(np.float64)
    recon = recon_y.astype(np.float64)

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            # 세그먼트 추출
            orig_seg = orig[y:y+block_size, x:x+block_size]
            recon_seg = recon[y:y+block_size, x:x+block_size]

            # 노이즈(오차) 계산
            noise = orig_seg - recon_seg
            signal_power = np.sum(orig_seg ** 2)
            noise_power = np.sum(noise ** 2)

            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                snr_values.append(snr)
            elif signal_power > 0:
                # 노이즈가 0인 경우(완전 일치) 매우 높은 SNR 부여
                snr_values.append(100.0)

    return np.mean(snr_values) if snr_values else 0
'''


def calculate_ssnr(orig_y, recon_y, block_size=16):
    """
    벡터화된 SSNR 계산: 2중 루프를 제거하고 NumPy 연산으로 대체
    """
    h, w = orig_y.shape
    # 블록 크기에 맞게 크기 조정 (나머지 부분 버림)
    h_new, w_new = (h // block_size) * block_size, (w // block_size) * block_size

    orig = orig_y[:h_new, :w_new].astype(np.float64)
    recon = recon_y[:h_new, :w_new].astype(np.float64)

    # 4D 배열로 재구성: (blocks_h, block_size, blocks_w, block_size)
    # 그 후 축을 변경하여 (blocks_h, blocks_w, block_size, block_size)로 만듦
    shape = (h_new // block_size, block_size, w_new // block_size, block_size)
    strides = orig.strides
    new_strides = (
        strides[0] * block_size,
        strides[0],
        strides[1] * block_size,
        strides[1],
    )

    orig_blocks = np.lib.stride_tricks.as_strided(
        orig, shape=shape, strides=new_strides
    )
    recon_blocks = np.lib.stride_tricks.as_strided(
        recon, shape=shape, strides=new_strides
    )

    # 신호 전력 및 노이즈 전력 계산 (블록별 sum)
    # axis (1, 3)은 각 블록의 height, width 방향임
    signal_power = np.sum(orig_blocks**2, axis=(1, 3))
    noise_power = np.sum((orig_blocks - recon_blocks) ** 2, axis=(1, 3))

    # 0으로 나누기 방지 및 SNR 계산
    # noise_power가 0인 곳은 100.0 (또는 매우 큰 값) 부여
    with np.errstate(divide="ignore", invalid="ignore"):
        snr = 10 * np.log10(signal_power / noise_power)
        snr[noise_power == 0] = 100.0  # 완전 일치하는 경우
        snr[np.isnan(snr)] = 0.0  # signal_power도 0인 경우 등 예외 처리

    return np.mean(snr)


# 1. 파일 전체를 메모리에 로드 (Y 채널만 3D 배열로 변환)
def _get_y_frames(frame_count, y_size, frame_size_bytes, width, height, path):
    raw_data = np.fromfile(path, dtype=np.uint8)
    # 각 프레임의 시작 위치 인덱스 계산
    starts = np.arange(frame_count) * frame_size_bytes
    # 모든 프레임의 Y 영역만 추출하여 (N, H, W) 형태로 reshape
    y_frames = np.array(
        [raw_data[s : s + y_size].reshape(height, width) for s in starts]
    )
    return y_frames.astype(np.float64)


def _read_yuv_frame(file, width, height):
    y_size = width * height
    uv_width, uv_height = width // 2, height // 2
    uv_size = uv_width * uv_height

    y_data = file.read(y_size)
    u_data = file.read(uv_size)
    v_data = file.read(uv_size)

    if not y_data or not u_data or not v_data:
        return None, None, None

    y = np.frombuffer(y_data, dtype=np.uint8).reshape((height, width))
    # Y 채널만 PSNR/SSIM 측정에 주로 사용되므로 U, V는 필요 시에만 리턴
    return y


def _calculate_bit_metrics(file_size_bytes, width, height, frame_count, fps=30):
    total_seconds = frame_count / fps
    bitrate_kbps = (file_size_bytes * 8) / (total_seconds * 1000)
    bpp = (file_size_bytes * 8) / (frame_count * width * height)
    return bitrate_kbps, bpp


if __name__ == "__main__":
    run_evaluate()
