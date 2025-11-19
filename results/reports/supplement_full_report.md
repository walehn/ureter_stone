# Supplementary Materials

## AI-Assisted Ureter Stone Detection:
## Statistical Analysis and Performance Evaluation

_Report Generated: 2025-11-19T22:57:17.146282_

---

# Executive Summary: AI-Assisted Ureter Stone Detection Performance

_Generated: 2025-11-19T22:57:17.146282_

## 🎯 Key Findings

### 1. Patient-level Performance (Primary Endpoint)

**BCR**:
- Sensitivity: -3.1%
- Specificity: +9.2%
- PPV: +8.7%
- NPV: -2.5%

**EMS**:
- Sensitivity: -11.4%
- Specificity: +41.6%
- PPV: +22.3%
- NPV: +5.2%

**Resident**:
- Sensitivity: +0.2%
- Specificity: +21.7%
- PPV: +20.6%
- NPV: +1.2%

### 2. Statistical Significance (GEE Analysis)

- **BCR**: OR = 1.074, p = 0.5471 ns
- **EMS**: OR = 2.165, p = 0.0000 ***
- **Resident**: OR = 1.502, p = 0.0001 ***

### 3. Clinical Utility (Decision Curve Analysis)

AI-assisted strategy showed superior net benefit across all readers:

- **BCR**: Max Δ Net Benefit = +0.0187
- **EMS**: Max Δ Net Benefit = +0.0955
- **Resident**: Max Δ Net Benefit = +0.0800

### 4. Lesion-level Detection Performance

**BCR**:
- Precision: +12.7%
- Recall: +0.0%
- F1 Score: +4.6%

**EMS**:
- Precision: +34.5%
- Recall: +1.5%
- F1 Score: +25.3%

**Resident**:
- Precision: +32.4%
- Recall: +6.4%
- F1 Score: +18.3%


---

# Table 1: Patient-level Performance Metrics

_AI-assisted vs Unaided Performance across Three Readers_

| Reader | Mode | N | Sensitivity | Specificity | PPV | NPV |
|--------|------|---|-------------|-------------|-----|-----|
| BCR | Unaided | 324 | 0.625 | 0.752 | 0.753 | 0.623 |
| BCR | **Assisted** | 324 | **0.594** | **0.843** | **0.841** | **0.598** |
| BCR | _Δ (Assisted - Unaided)_ | - | _-0.031_ | _+0.092_ | _+0.087_ | _-0.025_ |
| EMS | Unaided | 324 | 0.842 | 0.206 | 0.469 | 0.610 |
| EMS | **Assisted** | 324 | **0.728** | **0.622** | **0.692** | **0.662** |
| EMS | _Δ (Assisted - Unaided)_ | - | _-0.114_ | _+0.416_ | _+0.223_ | _+0.052_ |
| Resident | Unaided | 324 | 0.604 | 0.599 | 0.611 | 0.591 |
| Resident | **Assisted** | 324 | **0.605** | **0.816** | **0.818** | **0.603** |
| Resident | _Δ (Assisted - Unaided)_ | - | _+0.002_ | _+0.217_ | _+0.206_ | _+0.012_ |

_Note: Bold indicates AI-assisted performance. Δ shows the difference (Assisted - Unaided)._
_Positive Δ indicates improvement with AI assistance._


# Table 2: Bootstrap 95% Confidence Intervals for Performance Metrics

_B = 1000 iterations, patient-level resampling_

| Reader | Mode | Sensitivity (95% CI) | Specificity (95% CI) | PPV (95% CI) | NPV (95% CI) |
|--------|------|---------------------|---------------------|--------------|-------------|
| BCR | **Assisted** | 0.596 (0.544–0.646) | 0.843 (0.800–0.890) | 0.841 (0.797–0.889) | 0.599 (0.545–0.652) | 
| BCR | Unaided | 0.626 (0.569–0.682) | 0.751 (0.701–0.809) | 0.753 (0.699–0.806) | 0.623 (0.571–0.679) | 
| EMS | **Assisted** | 0.730 (0.681–0.780) | 0.621 (0.565–0.678) | 0.692 (0.645–0.741) | 0.663 (0.603–0.722) | 
| EMS | Unaided | 0.844 (0.798–0.889) | 0.208 (0.159–0.252) | 0.474 (0.427–0.521) | 0.611 (0.515–0.703) | 
| Resident | **Assisted** | 0.606 (0.554–0.656) | 0.816 (0.767–0.864) | 0.817 (0.769–0.866) | 0.604 (0.548–0.661) | 
| Resident | Unaided | 0.612 (0.557–0.670) | 0.600 (0.544–0.656) | 0.616 (0.561–0.673) | 0.596 (0.536–0.657) | 

_CI: Confidence Interval calculated using quantile method (2.5th and 97.5th percentiles)._


# Table 3: Generalized Estimating Equations (GEE) Analysis

_Cluster-robust inference with exchangeable correlation structure_

| Reader | Coefficient | OR | 95% CI | SE (Robust) | Z-score | P-value | Sig |
|--------|-------------|-----|--------|-------------|---------|---------|-----|
| BCR | 0.0716 | 1.074 | (0.851–1.356) | 0.1190 | 0.60 | 0.5471 | ns |
| EMS | 0.7722 | 2.165 | (1.680–2.789) | 0.1293 | 5.97 | 0.0000 | *** |
| Resident | 0.4071 | 1.502 | (1.231–1.833) | 0.1015 | 4.01 | 0.0001 | *** |

_OR: Odds Ratio for AI assistance effect. Significance: \*\*\* p<0.001, \*\* p<0.01, \* p<0.05, ns = not significant._
_Model: logit(P(positive)) = β₀ + β₁·(AI assisted)_


# Table 4: Decision Curve Analysis - Net Benefit Summary

_Maximum Net Benefit difference across threshold range (0.05–0.25)_

| Reader | Max Δ Net Benefit | Threshold at Max | Assisted NB | Unaided NB |
|--------|------------------|------------------|-------------|------------|
| BCR | +0.0187 | 0.250 | 0.3240 | 0.3053 |
| EMS | +0.0955 | 0.250 | 0.3344 | 0.2388 |
| Resident | +0.0800 | 0.250 | 0.3229 | 0.2430 |

_Δ Net Benefit = NB(Assisted) - NB(Unaided). Positive values indicate AI-assisted strategy is preferred._
_Threshold: Minimum probability at which intervention is warranted._


# Table 5: Lesion-level Detection Performance Metrics

_Object detection performance at individual lesion level_

| Reader | Mode | Precision | Recall | F1 Score |
|--------|------|-----------|--------|----------|
| BCR | Unaided | 0.699 | 0.564 | 0.625 |
| BCR | **Assisted** | **0.826** | **0.564** | **0.671** |
| BCR | _Δ (Assisted - Unaided)_ | _+0.127_ | _+0.000_ | _+0.046_ |
| EMS | Unaided | 0.264 | 0.624 | 0.371 |
| EMS | **Assisted** | **0.608** | **0.639** | **0.623** |
| EMS | _Δ (Assisted - Unaided)_ | _+0.345_ | _+0.015_ | _+0.253_ |
| Resident | Unaided | 0.438 | 0.505 | 0.469 |
| Resident | **Assisted** | **0.762** | **0.569** | **0.652** |
| Resident | _Δ (Assisted - Unaided)_ | _+0.324_ | _+0.064_ | _+0.183_ |

_Precision: TP/(TP+FP), Recall: TP/(TP+FN), F1: Harmonic mean of Precision and Recall._


---

# Statistical Methods

## Patient-level Analysis

Patient-level performance was assessed using standard diagnostic metrics:
- **Sensitivity**: TP / (TP + FN)
- **Specificity**: TN / (TN + FP)
- **Positive Predictive Value (PPV)**: TP / (TP + FP)
- **Negative Predictive Value (NPV)**: TN / (TN + FN)

## Bootstrap Analysis

To account for clustering within patients (multiple lesions per patient), we performed patient-level bootstrap resampling with B = 1000 iterations. 95% confidence intervals were calculated using the quantile method (2.5th and 97.5th percentiles of the bootstrap distribution).

## Generalized Estimating Equations (GEE)

Cluster-robust inference was performed using GEE with:
- **Family**: Binomial
- **Link function**: Logit
- **Correlation structure**: Exchangeable (within-patient correlation)
- **Model**: logit(P(Y=1)) = β₀ + β₁·(AI assisted)

Robust standard errors were calculated using the sandwich estimator.

## Decision Curve Analysis (DCA)

Clinical utility was assessed using DCA across threshold probabilities ranging from 0.05 to 0.25. Net benefit was calculated as:

**Net Benefit = (TP/N) - (FP/N) × [pt / (1 - pt)]**

where pt is the threshold probability. Positive net benefit differences indicate superior clinical utility of the AI-assisted strategy.

## Lesion-level Detection Metrics

Object detection performance was evaluated using:
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)


---

# Figures

All figures are available in the `results/figures/` directory:

- **Figure 1-3**: Decision Curve Analysis (BCR, EMS, Resident)
- **Figure 4-6**: Patient-level Metrics Comparison (BCR, EMS, Resident)
- **Figure 7-9**: Lesion-level Metrics Comparison (BCR, EMS, Resident)
- **Figure 10-12**: Precision-Recall Comparison (BCR, EMS, Resident)
- **Figure 13-18**: Confusion Matrices (BCR, EMS, Resident × Assisted/Unaided)
- **Figure 19-26**: Cross-reader Delta Comparisons

