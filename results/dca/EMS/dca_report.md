# Decision Curve Analysis Report

## Analysis Settings

- **Threshold Range**: [0.05, 0.25]
- **Number of Thresholds**: 50

## Sample Information

### Assisted (With AI)
- **N**: 321
- **Prevalence**: 0.539
- **Confusion Matrix**: TP=126, FP=56, FN=47, TN=92

### Unaided (Without AI)
- **N**: 321
- **Prevalence**: 0.455
- **Confusion Matrix**: TP=123, FP=139, FN=23, TN=36

## Net Benefit Summary

| Threshold | NB (Assisted) | NB (Unaided) | NB (Treat All) | Delta NB | Better Strategy |
|-----------|---------------|--------------|----------------|----------|------------------|
| 0.05 | 0.3833 | 0.3604 | 0.5147 | +0.0230 | Assisted |
| 0.10 | 0.3734 | 0.3356 | 0.4883 | +0.0378 | Assisted |
| 0.15 | 0.3622 | 0.3080 | 0.4589 | +0.0542 | Assisted |
| 0.20 | 0.3486 | 0.2742 | 0.4229 | +0.0744 | Assisted |
| 0.25 | 0.3344 | 0.2388 | 0.3853 | +0.0955 | Assisted |

## Clinical Interpretation

**AI assistance provides clinical benefit** across most threshold probabilities (100.0% of analyzed range).

**Maximum difference**: Δ Net Benefit = +0.0955 at threshold = 0.250
