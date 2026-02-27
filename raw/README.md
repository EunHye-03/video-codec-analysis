# Data Directory

이 폴더는 영상 분석 및 압축에 사용되는 데이터셋을 관리합니다.
보안 및 용량 문제로 실제 데이터는 Git에 포함되지 않습니다.

## 📁 구조 (Directory Structure)
- `raw/`: 원본 YUV 또는 MP4 영상 파일
- `compressed/`: VTM 인코딩 결과물 (.bin, .hevc, .vvc, .mp4)
- `decoded/`: VTM 디코딩 결과물 (.yuv)

## 📥 데이터셋 다운로드 가이드
본 프로젝트는 **ILSVRC 2015 Object Detection from Video (VID)** 데이터셋의 일부를 활용합니다.

1. **원본 데이터**: [ImageNet 공식 홈페이지](https://www.image-net.org/challenges/LSVRC/2015/) 또는 연구실 서버에서 다운로드하세요.
2. **대상 리스트**: `config.py`에 정의된 다음 파일들을 `raw/` 폴더 내에 배치해야 합니다.
   - `ILSVRC2015_val_00006001.yuv`
   - `ILSVRC2015_val_00041007.yuv`
   - (기타 config.py에 명시된 10종의 영상)

## ⚙️ 전처리 주의사항
- 본 스크립트는 원본 영상의 해상도를 4배 확대하여 처리하는 로직을 포함하고 있습니다.
- YUV 파일의 경우 **4:2:0 포맷**인지 확인해 주세요.
- 파일명이 `config.py`의 Key값과 일치해야 정상적으로 인식됩니다.