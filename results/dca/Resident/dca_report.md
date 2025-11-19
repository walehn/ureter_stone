# Decision Curve Analysis Report

## Analysis Settings

- **Threshold Range**: [0.05, 0.25]
- **Number of Thresholds**: 50

## Sample Information

### Assisted (With AI)
- **N**: 321
- **Prevalence**: 0.576
- **Confusion Matrix**: TP=112, FP=25, FN=73, TN=111

### Unaided (Without AI)
- **N**: 321
- **Prevalence**: 0.511
- **Confusion Matrix**: TP=99, FP=63, FN=65, TN=94

## Net Benefit Summary

| Threshold | NB (Assisted) | NB (Unaided) | NB (Treat All) | Delta NB | Better Strategy |
|-----------|---------------|--------------|----------------|----------|------------------|
| 0.05 | 0.3448 | 0.2981 | 0.5540 | +0.0467 | Assisted |
| 0.10 | 0.3404 | 0.2869 | 0.5298 | +0.0535 | Assisted |
| 0.15 | 0.3354 | 0.2743 | 0.5028 | +0.0611 | Assisted |
| 0.20 | 0.3293 | 0.2590 | 0.4697 | +0.0703 | Assisted |
| 0.25 | 0.3229 | 0.2430 | 0.4351 | +0.0800 | Assisted |

## Clinical Interpretation

**AI assistance provides clinical benefit** across most threshold probabilities (100.0% of analyzed range).

**Maximum difference**: Δ Net Benefit = +0.0800 at threshold = 0.250
