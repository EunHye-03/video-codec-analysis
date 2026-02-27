# Contributing to Video Codec Analysis Pipeline

이 프로젝트에 관심을 가져주셔서 감사합니다! 여러분의 기여는 프로젝트 발전에 큰 도움이 됩니다. 아래 가이드를 따라 기여해 주세요.

## 🐛 버그 제보 (Reporting Bugs)
버그를 발견하셨다면 [Issues](https://github.com/EunHye-03/video-codec-analysis/issues) 탭에 상세 내용을 남겨주세요.
- 버그가 발생하는 환경 (OS, Python 버전, VTM 버전)
- 재현 방법 (어떤 스크립트를 실행했을 때 에러가 났는지)
- 발생한 에러 메시지 캡처 또는 로그

## 💡 기능 제안 (Feature Requests)
새로운 분석 기능이나 시각화 방식이 필요하다면 Issue에 `enhancement` 라벨을 달아 제안해 주세요.

## 🛠 코드 기여 (Pull Request Process)
직접 코드를 수정하고 싶으시다면 다음 절차를 따라주세요.

1. 이 저장소를 **Fork** 합니다.
2. 새로운 기능을 위한 **Branch**를 생성합니다. (`git checkout -b feature/AmazingFeature`)
3. 코드 수정 후 **Commit** 합니다. (`git commit -m 'feat: Add some AmazingFeature'`)
4. 브랜치에 **Push** 합니다. (`git push origin feature/AmazingFeature`)
5. 원본 저장소에 **Pull Request**를 생성합니다.

## 📜 코딩 컨벤션
- 모든 스크립트는 `src/` 폴더 내에 위치해야 하며, 설정값은 `config.py`를 참조하도록 설계해 주세요.
- 새로운 라이브러리를 사용했다면 `requirements.txt`를 업데이트해 주세요.

---
함께 더 나은 영상 분석 도구를 만들어가길 기대합니다! 😊