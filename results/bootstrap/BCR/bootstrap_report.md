# Bootstrap Analysis Report

**Bootstrap Iterations**: 1000
**Confidence Level**: 95.0%
**Random Seed**: 42

## Assisted vs Unaided Performance

| Mode | Metric | Mean | Std | CI_Lower | CI_Upper | CI_95% |
|------|--------|------|-----|----------|----------|--------|
| Unaided | SENSITIVITY | 0.626 | 0.028 | 0.569 | 0.682 | [0.569, 0.682] |
| Unaided | SPECIFICITY | 0.751 | 0.027 | 0.701 | 0.809 | [0.701, 0.809] |
| Unaided | PPV | 0.753 | 0.028 | 0.699 | 0.806 | [0.699, 0.806] |
| Unaided | NPV | 0.623 | 0.028 | 0.571 | 0.679 | [0.571, 0.679] |
| Assisted | SENSITIVITY | 0.596 | 0.027 | 0.544 | 0.646 | [0.544, 0.646] |
| Assisted | SPECIFICITY | 0.843 | 0.024 | 0.800 | 0.890 | [0.800, 0.890] |
| Assisted | PPV | 0.841 | 0.024 | 0.797 | 0.889 | [0.797, 0.889] |
| Assisted | NPV | 0.599 | 0.027 | 0.545 | 0.652 | [0.545, 0.652] |
| Delta (A-U) | SENSITIVITY | -0.030 | 0.038 | -0.101 | 0.041 | [-0.101, +0.041] |
| Delta (A-U) | SPECIFICITY | 0.092 | 0.037 | 0.016 | 0.165 | [+0.016, +0.165] * |
| Delta (A-U) | PPV | 0.088 | 0.037 | 0.011 | 0.161 | [+0.011, +0.161] * |
| Delta (A-U) | NPV | -0.024 | 0.039 | -0.101 | 0.052 | [-0.101, +0.052] |


## Statistical Significance

**Significant improvements (95% CI excludes 0):**

- **SPECIFICITY**: Δ=+0.092 (95% CI: [+0.016, +0.165])
- **PPV**: Δ=+0.088 (95% CI: [+0.011, +0.161])
