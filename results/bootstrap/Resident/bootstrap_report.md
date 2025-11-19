# Bootstrap Analysis Report

**Bootstrap Iterations**: 1000
**Confidence Level**: 95.0%
**Random Seed**: 42

## Assisted vs Unaided Performance

| Mode | Metric | Mean | Std | CI_Lower | CI_Upper | CI_95% |
|------|--------|------|-----|----------|----------|--------|
| Unaided | SENSITIVITY | 0.612 | 0.029 | 0.557 | 0.670 | [0.557, 0.670] |
| Unaided | SPECIFICITY | 0.600 | 0.029 | 0.544 | 0.656 | [0.544, 0.656] |
| Unaided | PPV | 0.616 | 0.028 | 0.561 | 0.673 | [0.561, 0.673] |
| Unaided | NPV | 0.596 | 0.031 | 0.536 | 0.657 | [0.536, 0.657] |
| Assisted | SENSITIVITY | 0.606 | 0.027 | 0.554 | 0.656 | [0.554, 0.656] |
| Assisted | SPECIFICITY | 0.816 | 0.025 | 0.767 | 0.864 | [0.767, 0.864] |
| Assisted | PPV | 0.817 | 0.025 | 0.769 | 0.866 | [0.769, 0.866] |
| Assisted | NPV | 0.604 | 0.028 | 0.548 | 0.661 | [0.548, 0.661] |
| Delta (A-U) | SENSITIVITY | -0.005 | 0.039 | -0.085 | 0.065 | [-0.085, +0.065] |
| Delta (A-U) | SPECIFICITY | 0.215 | 0.039 | 0.141 | 0.297 | [+0.141, +0.297] * |
| Delta (A-U) | PPV | 0.201 | 0.038 | 0.128 | 0.275 | [+0.128, +0.275] * |
| Delta (A-U) | NPV | 0.008 | 0.041 | -0.074 | 0.092 | [-0.074, +0.092] |


## Statistical Significance

**Significant improvements (95% CI excludes 0):**

- **SPECIFICITY**: Δ=+0.215 (95% CI: [+0.141, +0.297])
- **PPV**: Δ=+0.201 (95% CI: [+0.128, +0.275])
