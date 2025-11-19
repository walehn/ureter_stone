# GEE Analysis Report

## Model Specification

- **Family**: Binomial
- **Link**: Logit
- **Correlation Structure**: Exchangeable
- **Working Correlation**: α=0.082

## Sample Information

- **N observations**: 650
- **N clusters (patients)**: 321
- **Mean cluster size**: 2.0
- **N covariates**: 2

## Coefficients

| Variable | Beta | SE (Robust) | z | P>|z| | OR | 95% CI (OR) |
|----------|------|-------------|---|-------|----|--------------|
| Intercept | -0.0185 | 0.1109 | -0.166 | 0.8678 | 0.982 | [0.790, 1.220] |
| Mode (Assisted vs Unaided) | 0.7722 | 0.1293 | 5.971 | 0.0000*** | 2.165 | [1.680, 2.789] |

**Significance codes**: *** p<0.001, ** p<0.01, * p<0.05

## Interpretation

**AI Assistance Effect**:

- **Odds Ratio**: 2.165
- **95% CI**: [1.680, 2.789]
- **P-value**: 0.0000

AI assistance **increases** the odds of positive detection by 116.5%.
