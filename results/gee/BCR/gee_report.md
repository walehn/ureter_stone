# GEE Analysis Report

## Model Specification

- **Family**: Binomial
- **Link**: Logit
- **Correlation Structure**: Exchangeable
- **Working Correlation**: α=0.101

## Sample Information

- **N observations**: 650
- **N clusters (patients)**: 321
- **Mean cluster size**: 2.0
- **N covariates**: 2

## Coefficients

| Variable | Beta | SE (Robust) | z | P>|z| | OR | 95% CI (OR) |
|----------|------|-------------|---|-------|----|--------------|
| Intercept | 0.7538 | 0.1185 | 6.360 | 0.0000*** | 2.125 | [1.684, 2.681] |
| Mode (Assisted vs Unaided) | 0.0716 | 0.1190 | 0.602 | 0.5471 | 1.074 | [0.851, 1.356] |

**Significance codes**: *** p<0.001, ** p<0.01, * p<0.05

## Interpretation

**AI Assistance Effect**:

- **Odds Ratio**: 1.074
- **95% CI**: [0.851, 1.356]
- **P-value**: 0.5471

AI assistance **increases** the odds of positive detection by 7.4%.
