import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config as cfg


def plot_rd_curves():
    # 1. 데이터 불러오기 (vcm/results/report/)
    hevc_path = os.path.join(cfg.OUTPUT_REPORT_DIR, "evaluation_HEVC.csv")
    vvc_path = os.path.join(cfg.OUTPUT_REPORT_DIR, "evaluation_VVC.csv")

    if not os.path.exists(hevc_path) or not os.path.exists(vvc_path):
        print("❌ CSV 파일이 없습니다. 평가를 먼저 진행해주세요.")
        return

    df_hevc = pd.read_csv(hevc_path)
    df_vvc = pd.read_csv(vvc_path)

    # [수정 포인트] inf 값을 처리합니다.
    # 1. inf를 NaN으로 바꾼 뒤
    df_hevc.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_vvc.replace([np.inf, -np.inf], np.nan, inplace=True)

    # 2. 방법 A: NaN(기존 inf)을 50dB(매우 좋은 화질)로 치환
    df_hevc["psnr"] = df_hevc["psnr"].fillna(50.0)
    df_vvc["psnr"] = df_vvc["psnr"].fillna(50.0)

    # 3. 혹은 방법 B: inf인 데이터를 그냥 빼버리고 평균 내기 (dropna)
    # df_hevc = df_hevc.dropna(subset=['psnr'])
    # df_vvc = df_vvc.dropna(subset=['psnr'])
    # 2. 영상별 평균 데이터 계산 (QP별로 모든 영상의 평균치 산출)
    hevc_avg = df_hevc.groupby("qp").mean(numeric_only=True).sort_values("bitrate_kbps")
    vvc_avg = df_vvc.groupby("qp").mean(numeric_only=True).sort_values("bitrate_kbps")

    # 3. 그래프 그리기 (PSNR, SSIM, SSNR)
    metrics = [
        ("psnr", "PSNR (dB)", "Rate-PSNR Curve"),
        ("ssim", "SSIM Index", "Rate-SSIM Curve"),
        ("ssnr", "SSNR (dB)", "Rate-SSNR Curve"),
    ]

    plt.figure(figsize=(18, 5))

    for i, (col, ylabel, title) in enumerate(metrics, 1):
        plt.subplot(1, 3, i)

        # HEVC 라인
        plt.plot(
            hevc_avg["bitrate_kbps"],
            hevc_avg[col],
            "o-",
            label="HEVC",
            color="tab:blue",
            markersize=8,
        )
        # VVC 라인
        plt.plot(
            vvc_avg["bitrate_kbps"],
            vvc_avg[col],
            "s--",
            label="VVC",
            color="tab:red",
            markersize=8,
        )

        plt.title(title, fontsize=14, fontweight="bold")
        plt.xlabel("Bitrate (kbps)", fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend()

    plt.tight_layout()

    # 그래프 저장 (vcm/results/report/)
    os.makedirs(cfg.OUTPUT_REPORT_DIR, exist_ok=True)
    save_path = os.path.join(cfg.OUTPUT_REPORT_DIR, "rd_curves_comparison.png")
    plt.savefig(save_path)
    print(f"✅ 그래프가 저장되었습니다: {save_path}")
    plt.close()


if __name__ == "__main__":
    plot_rd_curves()
