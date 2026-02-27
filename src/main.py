import config as cfg  # 설정 파일 로드
from step1_check_resolution import run_check_resolution
from step2_analyze_metrics import run_analyze_metrics
from step3_1_compress_hevc import run_compress_hevc
from step3_2_compress_vvc import run_compress_vvc
from step3_3_decode import run_decode
from step4_evaluate import run_evaluate
from step5_eval_visualizer import run_visualize


def main():
    print("🚀 해상도 체크 준비 중...")
    run_check_resolution(cfg.ROI_PATH)
    print("🚀 해상도 체크 완료...")

    print("🚀 메트릭 분석 준비 중...")
    run_analyze_metrics(cfg.ROI_PATH)
    print("🚀 메트릭 분석 완료...")

    print("🚀 HEVC 압축 준비 중...")
    run_compress_hevc()
    print("🚀 HEVC 압축 완료...")

    print("🚀 VVC 압축 준비 중...")
    run_compress_vvc()
    print("🚀 VVC 압축 완료...")

    print("🚀 DECODE 준비 중...")
    run_decode()
    print("🚀 DECODE 완료...")

    print("🚀 평가 준비 중...")
    run_evaluate()
    print("🚀 평가 완료...")

    print("🚀 시각화 준비 중...")
    run_visualize()
    print("🚀 시각화 완료...")


if __name__ == "__main__":
    main()
