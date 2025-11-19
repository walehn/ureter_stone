# Decision Curve Analysis Report

## Analysis Settings

- **Threshold Range**: [0.05, 0.25]
- **Number of Thresholds**: 50

## Sample Information

### Assisted (With AI)
- **N**: 321
- **Prevalence**: 0.583
- **Confusion Matrix**: TP=111, FP=21, FN=76, TN=113

### Unaided (Without AI)
- **N**: 321
- **Prevalence**: 0.548
- **Confusion Matrix**: TP=110, FP=36, FN=66, TN=109

## Net Benefit Summary

| Threshold | NB (Assisted) | NB (Unaided) | NB (Treat All) | Delta NB | Better Strategy |
|-----------|---------------|--------------|----------------|----------|------------------|
| 0.05 | 0.3424 | 0.3368 | 0.5606 | +0.0056 | Assisted |
| 0.10 | 0.3386 | 0.3304 | 0.5367 | +0.0082 | Assisted |
| 0.15 | 0.3344 | 0.3232 | 0.5101 | +0.0112 | Assisted |
| 0.20 | 0.3293 | 0.3145 | 0.4775 | +0.0149 | Assisted |
| 0.25 | 0.3240 | 0.3053 | 0.4434 | +0.0187 | Assisted |

## Clinical Interpretation

**AI assistance provides clinical benefit** across most threshold probabilities (100.0% of analyzed range).

**Maximum difference**: Δ Net Benefit = +0.0187 at threshold = 0.250
