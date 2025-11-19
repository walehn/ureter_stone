# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**요관 결석 탐지 AI 성능 분석 시스템**

이 프로젝트는 AI object detection 기반 요관 결석 탐지 연구의 통계 분석을 자동화합니다. 핵심 목표는 **Reviewer #3가 제기한 클러스터링 무시 및 유병률 왜곡 문제**를 cluster-robust 통계 기법으로 해결하는 것입니다.

**주요 분석**:
- 환자단위 성능 분석 (Sensitivity, Specificity, PPV, NPV)
- 병변단위 detection 성능 (Precision, Recall, F1, mAP)
- Cluster-robust patient-level bootstrap (≥1000 iterations)
- GEE robust inference
- Decision Curve Analysis

**모든 출력은 한국어로 작성합니다.**

## Data Files

**입력 데이터 (저장소 루트에 위치)**:
- `BCR_result.xlsx`: 영상의학전문의(Board-certified Radiologist) 결과
- `EMS_result.xlsx`: 응급의학과전문의(Emergency Medicine Specialist) 결과
- `Resident_result.xlsx`: 영상의학과전공의(Radiology Resident) 결과
- `results_summary.csv`: 요약 결과

**보안**: 모든 스프레드시트는 민감 정보(PHI)를 포함하며 외부 서비스 업로드를 금지합니다. 요약을 공유할 때는 식별자를 제거하세요.

## Planned Architecture

현재는 기획 단계이며, PRD.md에 따라 다음 구조로 개발될 예정입니다:

```
ureter_stone/
├── config/
│   └── analysis_config.yaml      # 전체 분석 파라미터 (bootstrap 횟수, IoU threshold 등)
├── data/
│   ├── BCR_result.xlsx
│   ├── EMS_result.xlsx
│   └── Resident_result.xlsx
├── src/
│   ├── data_loader.py            # FR-01: Excel 로딩 및 검증
│   ├── lesion_matching.py        # FR-02: IoU 기반 TP/FP/FN 매칭
│   ├── patient_metrics.py        # FR-03: 환자단위 Se/Sp/PPV/NPV
│   ├── bootstrap.py              # FR-04: Patient-level cluster-robust bootstrap
│   ├── gee_analysis.py           # FR-05: GEE(Binomial, Logit, Exchangeable)
│   ├── dca.py                    # FR-06: Decision Curve Analysis
│   ├── lesion_metrics.py         # FR-07: Lesion-level Precision/Recall/F1/mAP
│   ├── visualization.py          # FR-08: 모든 그래프 생성
│   └── reporter.py               # FR-09: Supplement-ready 출력 생성
├── results/
│   ├── tables/                   # CSV, Markdown 테이블
│   ├── figures/                  # 300 dpi PNG 그래프
│   └── summary.json              # 전체 수치 결과
├── tests/
│   └── test_*.py                 # pytest 기반 단위 테스트
├── main.py                       # 전체 파이프라인 실행
├── requirements.txt
├── PRD.md                        # 제품 요구사항 문서 (v1.1)
└── AGENTS.md                     # 기존 개발 가이드라인
```

## Development Setup

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 의존성 설치 (requirements.txt가 생성되면)
pip install -r requirements.txt

# 필수 패키지 (PRD.md 5.1절 참조):
# pandas, numpy, statsmodels, scikit-learn, scipy
# matplotlib, seaborn, openpyxl, PyYAML
```

## Analysis Pipeline Execution Flow

PRD.md 7.2절에 정의된 실행 순서:

1. **Load Config (YAML)**: `analysis_config.yaml` 파라미터 로딩
2. **Load Data (FR-01)**: Excel 파일 검증 및 로딩
3. **Lesion Matching (FR-02)**: IoU ≥ 0.5 기준 병변-예측 매칭
4. **Patient-level Metrics (FR-03)**: 환자단위 confusion matrix 생성
5. **Bootstrap Analysis (FR-04)**: B=1000, patient_id 단위 resampling
6. **GEE Analysis (FR-05)**: `logit(P(Y=1)) = β₀ + β₁·mode + β₂·reader_id`
7. **Decision Curve Analysis (FR-06)**: Threshold 0.05~0.25 범위 net benefit
8. **Lesion-level Metrics (FR-07)**: mAP@0.5, mAP@0.45 계산
9. **Visualization (FR-08)**: 5가지 주요 그래프 생성
10. **Generate Report (FR-09)**: Supplement-ready 출력물 생성

## Key Statistical Requirements

### Bootstrap (FR-04)
- **Resampling 단위**: `patient_id` (환자 클러스터 단위)
- **반복 횟수**: B ≥ 1000
- **신뢰구간**: Quantile-based 95% CI (2.5%, 97.5%)
- **Random seed 고정**: 재현성 보장

```python
# Pseudo-code
for b in range(B):
    resampled_patients = sample_with_replacement(patient_ids)
    Se_b, Sp_b, PPV_b, NPV_b = calculate_metrics(resampled_patients)
```

### GEE (FR-05)
- **Family**: Binomial
- **Link**: Logit
- **Correlation**: Exchangeable (환자 내 병변 간 상관관계 동일 가정)
- **Fixed effects**: mode (assisted vs unaided) + optional reader_id
- **구현**: `statsmodels.api.GEE` 사용

### IoU Matching (FR-02)
- **Threshold**: 0.5 (config에서 조정 가능)
- **매칭 알고리즘**: Greedy 또는 Hungarian (config 선택)
- **좌표 변환**: Polygon → BBox 지원

## Configuration (YAML)

전체 분석 파라미터는 `config/analysis_config.yaml`로 관리:

```yaml
analysis:
  bootstrap:
    n_iterations: 1000
    random_seed: 42
    confidence_level: 0.95

  matching:
    iou_threshold: 0.5
    algorithm: "greedy"  # or "hungarian"

  dca:
    threshold_min: 0.05
    threshold_max: 0.25
    n_points: 50

  gee:
    family: "binomial"
    link: "logit"
    correlation: "exchangeable"

output:
  directory: "./results"
  formats: ["csv", "png", "json", "markdown"]
  dpi: 300
```

## Performance Requirements

| 항목 | 목표 시간 |
|------|----------|
| Bootstrap 1000회 | 2-5분 이내 |
| GEE fitting | 1초 이내 |
| Lesion matching (1000개) | <1초 (vectorized 연산) |
| DCA curve 생성 | <1초 |
| 전체 파이프라인 | <10분 |

## Output Specification

**Supplement-ready 출력물** (FR-09):

| 항목 | 형식 | 설명 |
|------|------|------|
| Table 1 | CSV, Markdown | Patient-level confusion matrix |
| Table 2 | CSV, Markdown | Bootstrap 95% CI 요약 |
| Table 3 | CSV, Markdown | DCA summary (threshold별 net benefit) |
| Table 4 | CSV, Markdown | Lesion-level metrics (Precision, Recall, F1, mAP) |
| Figure 1 | PNG (300 dpi) | Bootstrap distribution |
| Figure 2 | PNG (300 dpi) | Decision Curve Analysis |
| Figure 3 | PNG (300 dpi) | Precision-Recall curve |
| Figure 4 | PNG (300 dpi) | Confusion Matrix Heatmap |
| Figure 5 | PNG (300 dpi) | Comparison Bar Chart (Assisted vs Unaided) |
| Code Appendix | Python, Markdown | IoU matching, Bootstrap, GEE 재현 코드 |

## Coding Conventions (from AGENTS.md)

**Python 스타일**:
- Python 3.8+ (PRD는 3.8+, AGENTS는 3.11+ 권장)
- 공백 4칸 들여쓰기
- `black` + `isort` 기본 설정 준수
- 커밋 전: `black scripts tests`

**파일명 규칙**:
- 스크립트: 동사+도메인 명사 (`clean_resident.py`, `sync_emergency_reports.py`)
- 테스트: `tests/test_<module>.py`
- 상수: `constants.py`에 집약

**Import 스타일**:
- 경로 기반 import 사용: `from modules.validators import score_ranges`
- 새 디렉터리에는 `__init__.py` 포함

**스프레드시트 컬럼명**:
- 도큐스트링에 원본 컬럼명을 그대로 인용하여 코드-데이터 싱크 유지

## Testing

```bash
# pytest 기반 테스트 (구현 시)
pytest tests/

# 단일 테스트 실행
pytest tests/test_bootstrap.py::test_resampling_unit

# 커버리지 확인
pytest --cov=src tests/
```

**테스트 전략**:
- 각 스프레드시트의 경계 사례 재현 (예: EMS 점수 누락)
- `results_summary.csv`의 기대 행 수·컬럼 단언
- 난수 기반 분석은 시드 고정 + `tests/data/` 스냅샷 저장
- 목표 코드 커버리지: ≥80%

## Linting (구현 예정)

```bash
# Makefile 타깃으로 구성 예정 (AGENTS.md 참조)
make lint  # black, isort, 타입 체크, 스키마 검증
```

## Commit Convention

Conventional Commit 형식 사용:
- `feat: add EMS variance check`
- `fix: correct BCR GPA merge`
- `docs: update PRD with FR-06 removal`
- `test: add bootstrap seed fixture`

PR 체크리스트:
- 임상 질문, 변경 데이터셋, 영향 범위 명시
- 스프레드시트 스키마 변경 시 스크린샷/요약 표 첨부
- 이슈 ID 참조 (`Refs #42`)
- 데이터 검증·테스트·PHI 비노출 확인

## Critical Implementation Notes

### 1. Cluster-robust Analysis
환자 내 여러 병변이 있을 수 있으므로:
- Bootstrap은 **반드시 patient_id 단위**로 resampling
- GEE는 **Exchangeable correlation** 사용
- 병변 단위(lesion-level)와 환자 단위(patient-level) 분석을 명확히 구분

### 2. Reproducibility
- 모든 난수 생성에 `random_seed` 설정
- Config 파일로 전체 파라미터 관리
- 실행 로그 자동 저장
- 동일 config → 동일 결과 보장

### 3. Supplement-ready Output
- 모든 표/그래프는 논문 제출 가능한 품질
- 300 dpi PNG 출력
- Color-blind friendly 색상
- 축 라벨, 범례 완비

## References

- **PRD.md (v1.1)**: 전체 제품 요구사항 및 기술 명세
- **AGENTS.md**: 개발 가이드라인 및 보안 정책
- **GEE**: Liang & Zeger (1986) - Longitudinal data analysis using generalized linear models
- **Bootstrap**: Efron & Tibshirani (1993) - An Introduction to the Bootstrap
- **DCA**: Vickers & Elkin (2006) - Decision curve analysis
