# 요관 결석 탐지 AI 성능 분석 결과

## 3개 리더 비교 분석

### BCR

**환자 수**: 324명

#### Without AI

- **Confusion Matrix**: TP=110, FP=36, FN=66, TN=109
- **Sensitivity**: 0.625 (62.5%)
- **Specificity**: 0.752 (75.2%)
- **PPV**: 0.753 (75.3%)
- **NPV**: 0.623 (62.3%)

#### With AI

- **Confusion Matrix**: TP=111, FP=21, FN=76, TN=113
- **Sensitivity**: 0.594 (59.4%)
- **Specificity**: 0.843 (84.3%)
- **PPV**: 0.841 (84.1%)
- **NPV**: 0.598 (59.8%)

#### Δ (With AI - Without AI)

- **SENSITIVITY**: -0.031 (-3.1%) ↓
- **SPECIFICITY**: +0.092 (+9.2%) ↑
- **PPV**: +0.087 (+8.7%) ↑
- **NPV**: -0.025 (-2.5%) ↓

---

### EMS

**환자 수**: 324명

#### Without AI

- **Confusion Matrix**: TP=123, FP=139, FN=23, TN=36
- **Sensitivity**: 0.842 (84.2%)
- **Specificity**: 0.206 (20.6%)
- **PPV**: 0.469 (46.9%)
- **NPV**: 0.610 (61.0%)

#### With AI

- **Confusion Matrix**: TP=126, FP=56, FN=47, TN=92
- **Sensitivity**: 0.728 (72.8%)
- **Specificity**: 0.622 (62.2%)
- **PPV**: 0.692 (69.2%)
- **NPV**: 0.662 (66.2%)

#### Δ (With AI - Without AI)

- **SENSITIVITY**: -0.114 (-11.4%) ↓
- **SPECIFICITY**: +0.416 (+41.6%) ↑
- **PPV**: +0.223 (+22.3%) ↑
- **NPV**: +0.052 (+5.2%) ↑

---

### Resident

**환자 수**: 324명

#### Without AI

- **Confusion Matrix**: TP=99, FP=63, FN=65, TN=94
- **Sensitivity**: 0.604 (60.4%)
- **Specificity**: 0.599 (59.9%)
- **PPV**: 0.611 (61.1%)
- **NPV**: 0.591 (59.1%)

#### With AI

- **Confusion Matrix**: TP=112, FP=25, FN=73, TN=111
- **Sensitivity**: 0.605 (60.5%)
- **Specificity**: 0.816 (81.6%)
- **PPV**: 0.818 (81.8%)
- **NPV**: 0.603 (60.3%)

#### Δ (With AI - Without AI)

- **SENSITIVITY**: +0.002 (+0.2%) ↑
- **SPECIFICITY**: +0.217 (+21.7%) ↑
- **PPV**: +0.206 (+20.6%) ↑
- **NPV**: +0.012 (+1.2%) ↑

---

