# Video Codec Analysis & Visualization Pipeline

이 프로젝트는 **HEVC/VVC(VTM)** 코덱을 활용한 영상 압축 성능 분석 및 시각화 자동화 도구입니다.
원본 YUV 영상의 특성 분석부터 압축, 복원, 그리고 성능 지표(PSNR 등)의 시각화까지 전 과정을 파이썬 스크립트로 제어합니다.

---

## 🚀 Key Features
- **Video Analysis**: 원본 영상의 해상도, 프레임, 비트레이트 특성 추출
- **VTM Automation**: VTM(VVC Test Model) Encoder/Decoder 실행 자동화
- **Batch Processing**: 다양한 QP(Quantization Parameter) 값에 대한 일괄 처리
- **Visualization**: 분석 결과를 차트 및 리포트(CSV)로 자동 생성

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Environment**: Ubuntu (WSL2)
- **Video Codec**: VTM (VVC), HM (HEVC)
- **Libraries**: OpenCV, NumPy, Matplotlib, Pandas

## 📂 Project Structure
```text
├── src/                # 분석 및 실행 소스 코드
├── raw/                # 영상 데이터 (Git 제외)
├── results/            # 시각화 차트 및 분석 리포트
├── config.py.template  # 환경 설정 템플릿
└── requirements.txt    # 의존성 라이브러리
```

---

# ⚙️ Setup & Installation

## 1. Repository Clone
```bash
git clone https://github.com/EunHye-03/video-codec-analysis.git
cd video-codec-analysis
```

## 2. Environment Setup
```bash
# 가상 환경 생성
python3 -m venv vcm_env
source vcm_env/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 3. VTM Build
```bash
# VTM 소스 코드 다운로드 (별도 진행)
# ...

# VTM 빌드 (VTM 폴더 내에서)
cd VTM
make clean
make -j8
```

---

# 🎯 Usage
## 1. Configuration
`src/config.py.template` 파일을 복사하여 `src/config.py`를 생성하고, 실제 경로와 설정을 수정하세요.

## 2. Run Analysis
```bash
# 분석 스크립트 실행
source vcm_env/bin/activate
python src/main.py
```

## 3. Output
결과는 `results/` 폴더에 자동으로 저장됩니다.
- csv 파일
- png 파일

---

# 🛠 Current Status
Ongoing: Modularizing scripts and upgrading the automation workflow.

---

# 🤝 Contributing
기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

---

# 📄 License
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 확인하세요.

---

# 📞 Support
문제가 발생하면 [Issues](https://github.com/EunHye-03/video-codec-analysis/issues)에 보고해주세요.
