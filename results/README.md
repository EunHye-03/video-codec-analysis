# Results Directory

이 폴더는 영상 분석 및 코덱 실행을 통해 생성된 모든 결과물을 저장합니다.
데이터의 성격에 따라 다음과 같이 하위 폴더로 구분됩니다.

## 📁 구조 (Directory Structure)
- `reports/`: 분석 결과가 담긴 CSV 및 텍스트 로그 파일
- `compressed/`: 인코딩을 통해 생성된 비트스트림 파일 (VVC/HEVC)
- `decoded/`: 인코딩 후 다시 복원된 YUV 영상 파일
- `evaluate/`: 품질 평가 지표(BD-rate 등) 요약 결과

## 📊 주요 리포트 파일 설명
| 파일명 | 설명 |
|:---|:---|
| `vcm_analysis_report.csv` | 영상 시퀀스별 비트레이트, 프레임 등의 기초 분석 결과 |
| `vcm_resolution_report.csv` | 원본 및 처리 대상 영상들의 해상도 매핑 리포트 |
| `check_resolution_report.csv` | 인코딩 전후 해상도 일치 여부 검증 로그 |
| `evaluation_HEVC.csv` | HEVC(HM) 코덱을 이용한 압축 성능 평가 결과 (PSNR 등) |
| `evaluation_VVC.csv` | VVC(VTM) 코덱을 이용한 압축 성능 평가 결과 (PSNR 등) |
| `metadata_vcm.csv` | 전체 실험 데이터셋에 대한 통합 메타데이터 정보 |
| `job_df.csv` | 실행된 작업(Job) 리스트 및 인코딩 파라미터 기록 |

## ⚠️ 주의사항
- `compressed/` 및 `decoded/` 폴더 내의 파일들은 용량이 매우 클 수 있습니다.
- 대용량 바이너리 파일은 원칙적으로 Git 추적에서 제외(`gitignore`)되어 있습니다.
- 최종 리포트(CSV)와 그래프(PNG) 위주로 성과를 관리하는 것을 권장합니다.
- 실험 데이터의 무결성을 위해 생성된 CSV 파일은 수동으로 수정하지 마시길 바랍니다.
- 새로운 실험 실행 시 기존 파일이 덮어씌워질 수 있으니 중요한 결과는 별도로 백업하시길 바랍니다.