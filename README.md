# 요관 결석 탐지 AI 성능 분석 시스템

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI object detection 기반 요관 결석 탐지 연구의 **통계 분석 자동화 시스템**입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [설치 방법](#설치-방법)
- [빠른 시작](#빠른-시작)
- [분석 파이프라인](#분석-파이프라인)
- [출력 결과](#출력-결과)
- [프로젝트 구조](#프로젝트-구조)
- [통계 방법론](#통계-방법론)
- [문제 해결](#문제-해결)

## 🎯 프로젝트 개요

본 시스템은 **Reviewer #3가 제기한 클러스터링 무시 및 유병률 왜곡 문제**를 cluster-robust 통계 기법으로 해결하기 위해 개발되었습니다.

### 핵심 목표

- ✅ **Patient-level 성능 분석** (Sensitivity, Specificity, PPV, NPV)
- ✅ **Lesion-level detection 성능** (Precision, Recall, F1, mAP)
- ✅ **Cluster-robust Bootstrap** (≥1000 iterations, patient-level resampling)
- ✅ **GEE robust inference** (Binomial family, Logit link, Exchangeable correlation)
- ✅ **Decision Curve Analysis** (Clinical utility evaluation)
- ✅ **Publication-ready outputs** (300 dpi figures, Supplement-ready tables)

### 연구 대상

**3명의 리더** × **2가지 모드** (AI-assisted vs Unaided):
- **BCR** (Board-certified Radiologist): 영상의학전문의
- **EMS** (Emergency Medicine Specialist): 응급의학과전문의
- **Resident** (Radiology Resident): 영상의학과전공의

**데이터**: 각 321-324명 환자, 총 ~970명의 CT 스캔

## ⚡ 주요 기능

### 1. 전체 분석 자동화
```bash
python3 main_simple.py
```
단일 명령으로 전체 분석 파이프라인 실행

### 2. Cluster-robust 통계
- Patient-level bootstrap resampling (B=1000)
- GEE with exchangeable correlation structure
- Sandwich variance estimator for robust SE

### 3. Publication-ready 출력
- 5개 Supplement 테이블 (Markdown, CSV)
- 26개 고해상도 그래프 (300 dpi PNG)
- Executive summary 자동 생성
- Methods section 자동 작성

### 4. 유연한 실행 옵션
```bash
# 전체 분석 (7-10분)
python3 main_simple.py

# Bootstrap 건너뛰기 (2-3분)
python3 main_simple.py --skip-bootstrap

# 분석만 (시각화 제외, 1-2분)
python3 main_simple.py --skip-visualization
```

## 🚀 설치 방법

### 필수 요구사항

- Python 3.9 이상
- pip (Python package manager)

### 1. 저장소 클론

```bash
git clone <repository-url>
cd ureter_stone
```

### 2. 가상환경 생성 (권장)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 데이터 파일 준비

Excel 파일을 프로젝트 루트에 배치:
- `BCR_result.xlsx`
- `EMS_result.xlsx`
- `Resident_result.xlsx`

## 📊 빠른 시작

### 전체 분석 실행

```bash
python3 main_simple.py
```

**출력 위치**:
- 최종 보고서: `results/reports/supplement_full_report.md`
- 그래프: `results/figures/`
- 통합 데이터: `results/reports/integrated_results.json`

### 개별 분석 실행

```bash
# 1. Patient-level 분석
python3 run_real_analysis.py

# 2. Bootstrap 분석 (B=1000, ~5분)
python3 run_bootstrap_analysis.py

# 3. GEE 분석
python3 run_gee_analysis.py

# 4. Decision Curve Analysis
python3 run_dca_analysis.py

# 5. Lesion-level 분석
python3 run_lesion_metrics.py

# 6. 시각화 생성
python3 run_visualization.py

# 7. 최종 보고서
python3 run_reporting.py
```

## 🔄 분석 파이프라인

```
📥 입력: Excel 파일 (BCR/EMS/Resident)
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Patient-level Metrics           │
│   - Sensitivity, Specificity, PPV, NPV  │
│   - Confusion Matrix                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 2: Bootstrap Analysis (B=1000)     │
│   - Patient-level resampling            │
│   - 95% Confidence Intervals            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 3: GEE Analysis                    │
│   - Cluster-robust inference            │
│   - Odds Ratios & p-values              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 4: Decision Curve Analysis         │
│   - Net Benefit calculation             │
│   - Clinical utility evaluation         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 5: Lesion-level Metrics            │
│   - Precision, Recall, F1 Score         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 6: Visualization (26 graphs)       │
│   - Decision curves                     │
│   - Performance comparisons             │
│   - Confusion matrices                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 7: Report Generation               │
│   - Supplement-ready report             │
│   - 5 tables + methods section          │
└─────────────────────────────────────────┘
    ↓
📤 출력: Supplement Materials
```

## 📁 출력 결과

### 디렉토리 구조

```
results/
├── analysis_results.json           # Patient-level 결과
├── bootstrap/                      # Bootstrap 분석
│   ├── BCR/
│   │   ├── bootstrap_results.json
│   │   ├── summary.csv
│   │   └── report.md
│   ├── EMS/
│   └── Resident/
├── gee/                           # GEE 분석
│   ├── BCR/
│   │   ├── gee_results.json
│   │   ├── coefficients.csv
│   │   └── report.md
│   ├── EMS/
│   └── Resident/
├── dca/                           # Decision Curve Analysis
│   ├── BCR/
│   │   ├── dca_results.json
│   │   ├── dca_curve.csv
│   │   └── summary.csv
│   ├── EMS/
│   └── Resident/
├── lesion_metrics/                # Lesion-level 성능
│   ├── BCR/
│   │   ├── lesion_metrics.json
│   │   ├── lesion_metrics.csv
│   │   └── lesion_metrics_report.md
│   ├── EMS/
│   └── Resident/
├── figures/                       # 26개 그래프 (300 dpi)
│   ├── BCR/
│   │   ├── decision_curve.png
│   │   ├── patient_metrics_comparison.png
│   │   ├── lesion_metrics_comparison.png
│   │   ├── precision_recall_comparison.png
│   │   ├── confusion_matrix_assisted.png
│   │   └── confusion_matrix_unaided.png
│   ├── EMS/
│   ├── Resident/
│   └── all_readers_*.png (8개)
└── reports/                       # 최종 보고서
    ├── supplement_full_report.md  # ★ Supplement-ready
    └── integrated_results.json    # 통합 JSON
```

### 주요 테이블

**Table 1: Patient-level Performance Metrics**
- 3개 리더 × 2개 모드 (Assisted/Unaided)
- Sensitivity, Specificity, PPV, NPV

**Table 2: Bootstrap 95% CI**
- B=1000 iterations
- Patient-level resampling

**Table 3: GEE Analysis Results**
- Odds Ratios with robust SE
- Cluster-robust p-values

**Table 4: DCA Summary**
- Maximum Net Benefit difference
- Optimal threshold

**Table 5: Lesion-level Detection**
- Precision, Recall, F1 Score

## 📂 프로젝트 구조

```
ureter_stone/
├── src/                           # 핵심 모듈
│   ├── bootstrap.py               # Bootstrap 분석
│   ├── gee_analysis.py            # GEE 구현
│   ├── dca.py                     # Decision Curve Analysis
│   ├── lesion_metrics.py          # Lesion-level 성능
│   ├── visualization.py           # 시각화
│   ├── reporter.py                # 보고서 생성
│   ├── patient_metrics.py         # Patient-level 분석
│   ├── logger.py                  # 로깅
│   └── constants.py               # 상수
├── run_*.py                       # 개별 실행 스크립트
├── main_simple.py                 # 통합 파이프라인
├── requirements.txt               # Python 의존성
├── CLAUDE.md                      # 프로젝트 가이드
├── PRD.md                         # 제품 요구사항
└── README.md                      # 본 문서
```

## 📊 통계 방법론

### Patient-level Analysis

```
Sensitivity = TP / (TP + FN)
Specificity = TN / (TN + FP)
PPV = TP / (TP + FP)
NPV = TN / (TN + FN)
```

### Bootstrap Analysis

- **Resampling 단위**: Patient ID (클러스터 단위)
- **반복 횟수**: B = 1000
- **신뢰구간**: Quantile method (2.5%, 97.5%)
- **Random seed**: 42 (재현성)

### GEE (Generalized Estimating Equations)

```
logit(P(Y=1)) = β₀ + β₁·(AI assisted)

- Family: Binomial
- Link: Logit
- Correlation: Exchangeable
- SE: Sandwich estimator (cluster-robust)
```

### Decision Curve Analysis

```
Net Benefit = (TP/N) - (FP/N) × [pt / (1 - pt)]

where pt = threshold probability (0.05-0.25)
```

### Lesion-level Metrics

```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 Score = 2 × (Precision × Recall) / (Precision + Recall)
```

## 🔧 문제 해결

### pandas/numpy 버전 충돌

**증상**: `ImportError: this version of pandas is incompatible with numpy`

**해결책**: 본 프로젝트는 pandas를 사용하지 않도록 설계되었습니다.
```bash
# openpyxl만으로 Excel 로딩
pip install openpyxl numpy scipy matplotlib
```

### Bootstrap JSON 파일 손상

**증상**: `JSONDecodeError: Expecting value`

**해결책**: Bootstrap 재실행
```bash
python3 run_bootstrap_analysis.py
```

### 메모리 부족

**증상**: Bootstrap 중 메모리 초과

**해결책**: Iteration 수 줄이기
```python
# src/bootstrap.py
analyzer = BootstrapAnalyzer(n_iterations=100)  # 기본 1000 → 100
```

## 📝 주요 발견사항 (예시)

### EMS (응급의학과전문의)
- **Specificity**: +41.6% 🔥
- **Precision**: +34.5%
- **OR**: 2.165*** (p < 0.001)
- **해석**: AI가 과다 진단(FP)을 대폭 줄임

### Resident (전공의)
- **Specificity**: +21.7%
- **Precision**: +32.4%
- **OR**: 1.502*** (p < 0.001)
- **해석**: 경험 부족을 AI가 효과적으로 보완

### BCR (영상의학전문의)
- **Specificity**: +9.2%
- **Precision**: +12.7%
- **OR**: 1.074 (p = 0.547, ns)
- **해석**: 이미 높은 baseline으로 AI 추가 이득 제한적

## 📚 참고 문헌

- **Bootstrap**: Efron & Tibshirani (1993) - An Introduction to the Bootstrap
- **GEE**: Liang & Zeger (1986) - Longitudinal data analysis using generalized linear models
- **DCA**: Vickers & Elkin (2006) - Decision curve analysis

## 🤝 기여

본 프로젝트는 연구 목적으로 개발되었습니다. 기여는 환영합니다!

## 📄 라이선스

MIT License

## 👥 개발자

- Claude Code (Anthropic)
- 개발 기간: 2025년 1월

## 📞 문의

프로젝트 관련 문의사항은 이슈로 등록해 주세요.

---

**마지막 업데이트**: 2025-11-16
**버전**: 1.0.0
