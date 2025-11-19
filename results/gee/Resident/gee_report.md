# GEE Analysis Report

## Model Specification

- **Family**: Binomial
- **Link**: Logit
- **Correlation Structure**: Exchangeable
- **Working Correlation**: α=0.134

## Sample Information

- **N observations**: 650
- **N clusters (patients)**: 321
- **Mean cluster size**: 2.0
- **N covariates**: 2

## Coefficients

| Variable | Beta | SE (Robust) | z | P>|z| | OR | 95% CI (OR) |
|----------|------|-------------|---|-------|----|--------------|
| Intercept | 0.4183 | 0.1131 | 3.697 | 0.0002*** | 1.519 | [1.217, 1.897] |
| Mode (Assisted vs Unaided) | 0.4071 | 0.1015 | 4.011 | 0.0001*** | 1.502 | [1.231, 1.833] |

**Significance codes**: *** p<0.001, ** p<0.01, * p<0.05

## Interpretation

**AI Assistance Effect**:

- **Odds Ratio**: 1.502
- **95% CI**: [1.231, 1.833]
- **P-value**: 0.0001

AI assistance **increases** the odds of positive detection by 50.2%.
