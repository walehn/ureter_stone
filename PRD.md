# Product Requirements Document (PRD)
## AI Object Detection 기반 의학 연구 분석 시스템 - 요관 결석 탐지

**버전**: 1.2
**작성일**: 2025-11-14
**상태**: Draft

---

## 1. 제품 개요 (Product Overview)

### 1.1 목적

이 시스템은 **AI object detection 기반 의학 연구(요관 결석 탐지)**의 결과물을 활용하여 다음 분석을 자동화하는 것을 목표로 합니다:

- **환자단위 성능 분석** (Primary)
- **환자단위 cluster-robust 부트스트랩**
- **GEE robust inference**
- **Decision Curve Analysis**


### 1.2 사용 대상

- 의료 인공지능 연구자
- Radiology reader study 분석자
- Detection-based AI 과제 통계 검증 담당자
- Reviewer 대응 및 재현성 패키지 자동화 필요자

### 1.3 핵심 가치

- **통계적 엄밀성**: Cluster-robust inference로 클러스터링 문제 해결
- **재현성**: 전체 분석 파이프라인의 완전한 재현 가능
- **자동화**: 수동 분석 시간을 90% 이상 절감
- **검증 가능성**: Supplement-ready 출력으로 peer review 대응 강화

---

## 2. 목표 (Goals)

### 2.1 Primary Goals

| ID | 목표 | 성공 지표 |
|----|------|----------|
| G-01 | 환자단위 지표(Sensitivity, Specificity, PPV, NPV)의 cluster-robust 분석 완전 자동화 | 수동 개입 없이 분석 완료 |
| G-02 | Patient-level bootstrap (≥1000 iterations) 자동 실행 및 95% CI 생성 | 2-5분 내 완료 |
| G-03 | GEE(exchangeable) 기반 patient-level inference 제공 | OR, 95% CI, p-value 자동 출력 |
| G-04 | Decision Curve Analysis 자동 생성 | Net Benefit curve 및 비교 그래프 생성 |

### 2.2 Secondary Goals

| ID | 목표 | 성공 지표 |
|----|------|----------|
| G-05 | Lesion-level detection 성능(Precision, Recall, F1, mAP) 자동 계산 | 모든 지표 자동 산출 |
| G-06 | 클래스 혼동 분석 자동 작성 | Confusion matrix 자동 생성 |

### 2.3 Reproducibility Goals

| ID | 목표 | 성공 지표 |
|----|------|----------|
| G-08 | 전체 분석 pipeline을 JSON/YAML config 기반으로 재현 가능하도록 구성 | 동일 config로 동일 결과 재현 |
| G-09 | Supplement-ready output 자동 생성 (표, 그림, code snippet) | 논문 제출 가능한 품질의 출력물 |

---

## 3. 제약사항 및 가정 (Constraints & Assumptions)

### 3.1 제약사항

- Python 3.8 이상 환경에서 동작
- GPU 불필요 (CPU 기반 처리)
- 입력 데이터는 특정 형식의 Excel 파일로 제공
- 처리 시간: Bootstrap 1000회 기준 5분 이내

### 3.2 가정

- 입력 데이터는 사전 정의된 스키마를 따름
- Patient ID는 고유하며 중복 없음
- 결측치는 사전 처리되어 있음

---

## 4. 분석 기능 요구사항 (Functional Requirements)

### 4.1 데이터 입력 처리 (FR-01)

**입력 데이터**

결과 스프레드시트는 저장소 루트에 존재하며, 다음 형식을 따릅니다:

| 파일명 | 설명 | 리더 유형 |
|--------|------|----------|
| `BCR_result.xlsx` | 영상의학전문의 결과 | Board-certified Radiologist |
| `EMS_result.xlsx` | 응급의학과전문의 결과 | Emergency Medicine Specialist |
| `Resident_result.xlsx` | 영상의학과전공의 결과 | Radiology Resident |

**요구사항**

- Excel 파일 자동 로딩 및 검증
- 스키마 일치 여부 확인
- 결측치 및 이상치 탐지
- 데이터 타입 자동 변환

**출력**

- 로딩 상태 리포트 (성공/실패, 레코드 수)
- 데이터 품질 체크 결과

---

### 4.2 환자단위 지표 계산 (FR-02)

**자동 계산 지표**

| 지표 | 공식 | 설명 |
|------|------|------|
| Sensitivity | TP / (TP + FN) | 환자단위 민감도 |
| Specificity | TN / (TN + FP) | 환자단위 특이도 |
| PPV | TP / (TP + FP) | 양성 예측도 |
| NPV | TN / (TN + FN) | 음성 예측도 |
| Δ(assisted − unaided) | Se_assisted - Se_unaided | AI 보조 효과 |

**Case-level Confusion Matrix**

자동 생성되는 환자단위 confusion matrix:

|  | Predicted Positive | Predicted Negative |
|--|-------------------|-------------------|
| **Actual Positive** | TP_patient | FN_patient |
| **Actual Negative** | FP_patient | TN_patient |

**출력**

- 지표별 point estimate
- Confusion matrix (CSV, PNG)
- 비교 테이블 (assisted vs unaided)

---

### 4.3 Cluster-robust Patient-level Bootstrap (FR-03)

**목적**

환자 클러스터링을 고려한 robust 신뢰구간 추정

**요구사항**

- **Resampling 단위**: `patient_id` (환자 단위)
- **Bootstrap iterations**: B ≥ 1000
- 각 반복에서 Se*, Sp*, PPV*, NPV* 계산
- **95% CI 생성**: Quantile-based (2.5%, 97.5%)
- 재현성을 위한 random seed 설정 옵션

**알고리즘**

```python
# Pseudo-code
for b in range(B):
    resampled_patients = sample_with_replacement(patient_ids)
    Se_b, Sp_b = calculate_metrics(resampled_patients)
    store(Se_b, Sp_b)

CI_Se = percentile(Se_bootstrap, [2.5, 97.5])
CI_Sp = percentile(Sp_bootstrap, [2.5, 97.5])
```

**출력**

- Bootstrap 결과 CSV (iteration별 지표값)
- 95% CI 요약 테이블
- Bootstrap distribution plot (histogram + CI)

---

### 4.4 GEE Robust Analysis (FR-04)

**목적**

Generalized Estimating Equations를 이용한 cluster-robust inference

**모델 설정**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| Family | Binomial | 이진 분류 |
| Link | Logit | Logistic regression |
| Correlation | Exchangeable | 환자 내 병변 간 상관관계 동일 가정 |
| Fixed effects | mode (+ optional reader_id) | AI 보조 여부 (+ 리더 ID) |

**수식**

```
logit(P(Y=1)) = β₀ + β₁·mode + β₂·reader_id (optional)
```

**출력**

- OR (assisted vs unaided)
- 95% CI (robust standard error 기반)
- p-value
- 모델 적합도 지표 (QIC)

---

### 4.5 Decision Curve Analysis (FR-05)

**목적**

임상적 의사결정 threshold에 따른 net benefit 분석

**입력**

- Patient-level predictions (assisted vs unaided)
- Threshold probability grid (예: 0.05~0.25)

**계산**

```
Net Benefit = (TP/N) - (FP/N) × (p_t / (1 - p_t))
```

where `p_t` is the threshold probability.

**출력**

- Net Benefit curve (threshold 범위)
- Assisted vs Unaided 비교
- Bootstrap confidence band (optional)
- 최적 threshold 제안

---

### 4.6 Lesion-level Metrics (FR-06)

**자동 계산 지표**

| 지표 | 공식 | 설명 |
|------|------|------|
| Precision | TP / (TP + FP) | 병변단위 정밀도 |
| Recall | TP / (TP + FN) | 병변단위 재현율 |
| F1 | 2 × (Precision × Recall) / (Precision + Recall) | F1 score |
| mAP@0.5 | Mean Average Precision at IoU=0.5 | 탐지 성능 종합 지표 |
| mAP@0.45 | Mean Average Precision at IoU=0.45 | 낮은 threshold |

**출력**

- Lesion-level metrics 테이블
- Precision-Recall curve
- mAP 계산 상세 로그

---

### 4.7 시각화 및 그래프 (FR-07)

**요구사항**

모든 주요 지표에 대한 시각화 자동 생성

**그래프 목록**

1. **Bootstrap Distribution**: Histogram + 95% CI 표시
2. **Decision Curve**: Net benefit vs threshold
3. **Precision-Recall Curve**: Lesion-level 성능
4. **Confusion Matrix Heatmap**: 환자단위 및 병변단위
5. **Comparison Bar Chart**: Assisted vs Unaided

**요구사항**

- 고해상도 PNG (300 dpi)
- 일관된 color scheme
- 논문 제출 가능한 품질
- 축 라벨, 범례 완비

---

### 4.8 Reporting Package (FR-08)

**목적**

논문 supplement에 즉시 사용 가능한 출력물 생성

**Supplement-ready 출력**

| 항목 | 형식 | 설명 |
|------|------|------|
| Table 1 | CSV, Markdown | Patient-level confusion matrix |
| Table 2 | CSV, Markdown | Bootstrap CI 요약 |
| Table 3 | CSV, Markdown | DCA summary (threshold별 net benefit) |
| Table 4 | CSV, Markdown | Lesion-level metrics |
| Figure 1 | PNG | Bootstrap distribution |
| Figure 2 | PNG | Decision Curve Analysis |
| Figure 3 | PNG | Precision-Recall curve |
| Figure 4 | PNG | Confusion Matrix Heatmap |
| Figure 5 | PNG | Comparison Bar Chart |
| Code Appendix | Python, Markdown | Bootstrap, GEE 재현 코드 |

**추가 출력**

- JSON summary: 모든 수치 결과 통합
- Analysis report: PDF 형식의 종합 리포트
- Reproducibility package: Config + data + code

---

## 5. 기술 요구사항 (Technical Requirements)

### 5.1 개발 환경 (TR-01)

**언어 및 프레임워크**

- Python ≥ 3.8
- 필수 라이브러리:
  - `pandas`: 데이터 처리
  - `numpy`: 수치 계산
  - `statsmodels`: GEE 분석
  - `scikit-learn`: 메트릭 계산
  - `scipy`: 통계 분석
  - `matplotlib`, `seaborn`: 시각화
  - `openpyxl`: Excel 파일 처리
  - `PyYAML`: 설정 파일 처리

### 5.2 GEE 모듈 (TR-02)

**요구사항**

- `statsmodels.api.GEE` 사용
- Family: Binomial
- Link: Logit
- Correlation: Exchangeable

**함수 시그니처**

```python
def fit_gee_model(
    data: pd.DataFrame,
    formula: str,
    groups: str,
    family: sm.families.Family = sm.families.Binomial()
) -> GEEResults:
    """Fit GEE model and return results"""
    pass
```

### 5.3 시각화 모듈 (TR-03)

**요구사항**

- Matplotlib/Seaborn 기반
- 일관된 스타일 (논문 품질)
- 300 dpi PNG 출력
- 색상 선택: Color-blind friendly

**스타일 가이드**

```python
# Plot settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
```

### 5.4 설정 파일 (TR-04)

**YAML Config 구조**

```yaml
analysis:
  bootstrap:
    n_iterations: 1000
    random_seed: 42
    confidence_level: 0.95

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
  high_res: true
  dpi: 300
```

### 5.5 출력 형식 (TR-05)

**모든 결과 Export 형태**

| 형식 | 용도 | 예시 |
|------|------|------|
| CSV | 테이블 데이터 | `bootstrap_results.csv` |
| PNG | 그래프 및 시각화 | `dca_curve.png` |
| JSON | 수치 결과 요약 | `summary.json` |
| Markdown | 리포트 문서 | `analysis_report.md` |

---

## 6. 비기능 요구사항 (Non-functional Requirements)

### 6.1 성능 요구사항 (Performance Requirements)

| 항목 | 요구치 | 측정 방법 |
|------|--------|----------|
| Bootstrap 1000회 | 2-5분 이내 | 실행 시간 측정 |
| GEE fitting | 1초 이내 | 함수 실행 시간 |
| DCA curve 생성 | <1초 | 계산 및 plot 시간 |
| 전체 파이프라인 | <10분 | 입력부터 출력까지 |

### 6.2 재현성 (Reproducibility)

- Random seed 설정 가능
- 모든 파라미터 config 파일로 관리
- 버전 관리 (데이터, 코드, 결과)
- 실행 로그 자동 저장

### 6.3 확장성 (Scalability)

- 다양한 리더 수 지원 (3명 이상)
- 다양한 질환/모달리티 적용 가능
- 추가 지표 계산 모듈화

### 6.4 사용성 (Usability)

- CLI 인터페이스 제공
- 진행 상황 표시 (progress bar)
- 명확한 에러 메시지
- 사용 가이드 문서 제공

### 6.5 신뢰성 (Reliability)

- 입력 데이터 검증
- 에러 핸들링 및 로깅
- 중간 결과 저장 (체크포인트)
- 실패 시 복구 가능

---

## 7. 시스템 아키텍처

### 7.1 모듈 구조

```
ureter_stone/
├── config/
│   └── analysis_config.yaml
├── data/
│   ├── BCR_result.xlsx
│   ├── EMS_result.xlsx
│   └── Resident_result.xlsx
├── src/
│   ├── data_loader.py         # FR-01
│   ├── patient_metrics.py     # FR-02
│   ├── bootstrap.py           # FR-03
│   ├── gee_analysis.py        # FR-04
│   ├── dca.py                 # FR-05
│   ├── lesion_metrics.py      # FR-06
│   ├── visualization.py       # FR-07
│   └── reporter.py            # FR-08
├── results/
│   ├── tables/
│   ├── figures/
│   └── summary.json
├── main.py
└── README.md
```

### 7.2 실행 흐름

```
1. Load Config (YAML)
   ↓
2. Load Data (FR-01)
   ↓
3. Patient-level Metrics (FR-02)
   ↓
4. Bootstrap Analysis (FR-03)
   ↓
5. GEE Analysis (FR-04)
   ↓
6. Decision Curve Analysis (FR-05)
   ↓
7. Lesion-level Metrics (FR-06)
   ↓
8. Visualization (FR-07)
   ↓
9. Generate Report (FR-08)
```

---

## 8. 성공 지표 (Success Metrics)

### 8.1 정량적 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 분석 시간 단축 | 90% 이상 | 수동 분석 대비 시간 비교 |
| 재현성 | 100% | 동일 config로 동일 결과 재현 |
| 코드 커버리지 | ≥80% | Unit test coverage |
| 문서화 완성도 | 100% | 모든 함수 docstring 작성 |

### 8.2 정성적 지표

- Reviewer 의견에 완전 대응 가능
- 논문 supplement 직접 활용 가능
- 다른 연구자의 재사용 가능
- 통계 검증 통과

---

## 9. 일정 및 마일스톤 (Timeline & Milestones)

| 마일스톤 | 설명 | 예상 기간 |
|----------|------|----------|
| M1: 데이터 로딩 및 검증 | FR-01 구현 | 1주 |
| M2: Patient metrics | FR-02 구현 | 1주 |
| M3: Bootstrap | FR-03 구현 | 1주 |
| M4: GEE 분석 | FR-04 구현 | 1주 |
| M5: DCA 분석 | FR-05 구현 | 1주 |
| M6: Lesion metrics | FR-06 구현 | 1주 |
| M7: 시각화 | FR-07 구현 | 1주 |
| M8: Reporting | FR-08 구현 | 1주 |
| M9: 테스트 및 문서화 | 통합 테스트, README | 1주 |

**총 예상 기간**: 9주

---

## 10. 리스크 및 완화 전략 (Risks & Mitigation)

| 리스크 | 영향 | 완화 전략 |
|--------|------|----------|
| 입력 데이터 형식 불일치 | High | 엄격한 스키마 검증 및 에러 메시지 |
| Bootstrap 계산 시간 초과 | Medium | 병렬 처리 또는 최적화 |
| GEE 수렴 실패 | Medium | 초기값 설정 옵션 제공 |
| 메모리 부족 (대용량 데이터) | Low | Chunking 또는 out-of-core 처리 |
| 통계 검증 오류 | High | 외부 전문가 리뷰, 단위 테스트 |

---

## 11. 의존성 (Dependencies)

### 11.1 외부 의존성

- Python 패키지 (requirements.txt 관리)
- Excel 파일 형식 호환성
- OS: Linux, macOS, Windows 지원

### 11.2 내부 의존성

- 데이터 로딩 → 모든 분석 모듈
- Patient metrics → Bootstrap, GEE, DCA

---

## 12. 참고 문헌 (References)

- **GEE**: Liang & Zeger (1986) - Longitudinal data analysis using generalized linear models
- **Bootstrap**: Efron & Tibshirani (1993) - An Introduction to the Bootstrap
- **DCA**: Vickers & Elkin (2006) - Decision curve analysis: a novel method for evaluating prediction models
- **mAP**: Mean Average Precision for detection tasks

---

## 13. 변경 이력 (Change Log)

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2025-11-14 | 초안 작성 | Claude |
| 1.1 | 2025-11-14 | FR-06 (유병률 조정 PPV/NPV 분석) 삭제 및 전체 넘버링 재정렬 | Claude |
| 1.2 | 2025-11-14 | FR-02 (Lesion-level Matching) 삭제. Lesion-level Metrics는 FR-06으로 유지 | Claude |

---

## 14. 승인 (Approval)

| 역할 | 이름 | 승인 날짜 | 서명 |
|------|------|----------|------|
| Product Owner |  |  |  |
| Technical Lead |  |  |  |
| Statistician |  |  |  |

---

**문서 종료**
