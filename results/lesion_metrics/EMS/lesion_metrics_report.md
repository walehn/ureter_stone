# Lesion-level Performance Metrics Report

## Summary Table

| Strategy | TP | FP | FN | Precision | Recall | F1 Score |
|----------|----|----|----|-----------| -------|----------|
| Assisted (With AI) | 258 | 166 | 146 | 0.6085 | 0.6386 | 0.6232 |
| Unaided (Without AI) | 252 | 704 | 152 | 0.2636 | 0.6238 | 0.3706 |
| Δ (Assisted - Unaided) | +6 | -538 | -6 | +0.3449 | +0.0149 | +0.2526 |

## Detailed Metrics

### Assisted (With AI)

- **True Positives (TP)**: 258 lesions
- **False Positives (FP)**: 166 lesions
- **False Negatives (FN)**: 146 lesions
- **Total Detections**: 424 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.6085 (60.85%)
- **Recall**: 0.6386 (63.86%)
- **F1 Score**: 0.6232 (62.32%)

### Unaided (Without AI)

- **True Positives (TP)**: 252 lesions
- **False Positives (FP)**: 704 lesions
- **False Negatives (FN)**: 152 lesions
- **Total Detections**: 956 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.2636 (26.36%)
- **Recall**: 0.6238 (62.38%)
- **F1 Score**: 0.3706 (37.06%)

## Interpretation

**AI assistance improves lesion-level detection performance.**

- **Precision change**: +0.3449 (+34.49%)
- **Recall change**: +0.0149 (+1.49%)
- **F1 Score change**: +0.2526 (+25.26%)

**Win-win**: AI improves both precision and recall!
