# Bootstrap Analysis Report

**Bootstrap Iterations**: 1000
**Confidence Level**: 95.0%
**Random Seed**: 42

## Assisted vs Unaided Performance

| Mode | Metric | Mean | Std | CI_Lower | CI_Upper | CI_95% |
|------|--------|------|-----|----------|----------|--------|
| Unaided | SENSITIVITY | 0.844 | 0.023 | 0.798 | 0.889 | [0.798, 0.889] |
| Unaided | SPECIFICITY | 0.208 | 0.024 | 0.159 | 0.252 | [0.159, 0.252] |
| Unaided | PPV | 0.474 | 0.024 | 0.427 | 0.521 | [0.427, 0.521] |
| Unaided | NPV | 0.611 | 0.049 | 0.515 | 0.703 | [0.515, 0.703] |
| Assisted | SENSITIVITY | 0.730 | 0.026 | 0.681 | 0.780 | [0.681, 0.780] |
| Assisted | SPECIFICITY | 0.621 | 0.030 | 0.565 | 0.678 | [0.565, 0.678] |
| Assisted | PPV | 0.692 | 0.025 | 0.645 | 0.741 | [0.645, 0.741] |
| Assisted | NPV | 0.663 | 0.031 | 0.603 | 0.722 | [0.603, 0.722] |
| Delta (A-U) | SENSITIVITY | -0.115 | 0.035 | -0.184 | -0.044 | [-0.184, -0.044] * |
| Delta (A-U) | SPECIFICITY | 0.413 | 0.038 | 0.342 | 0.491 | [+0.342, +0.491] * |
| Delta (A-U) | PPV | 0.218 | 0.034 | 0.154 | 0.288 | [+0.154, +0.288] * |
| Delta (A-U) | NPV | 0.051 | 0.059 | -0.061 | 0.170 | [-0.061, +0.170] |


## Statistical Significance

**Significant improvements (95% CI excludes 0):**

- **SENSITIVITY**: Δ=-0.115 (95% CI: [-0.184, -0.044])
- **SPECIFICITY**: Δ=+0.413 (95% CI: [+0.342, +0.491])
- **PPV**: Δ=+0.218 (95% CI: [+0.154, +0.288])
