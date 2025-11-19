# Lesion-level Performance Metrics Report

## Summary Table

| Strategy | TP | FP | FN | Precision | Recall | F1 Score |
|----------|----|----|----|-----------| -------|----------|
| Assisted (With AI) | 228 | 48 | 176 | 0.8261 | 0.5644 | 0.6706 |
| Unaided (Without AI) | 228 | 98 | 176 | 0.6994 | 0.5644 | 0.6247 |
| Δ (Assisted - Unaided) | +0 | -50 | +0 | +0.1267 | +0.0000 | +0.0459 |

## Detailed Metrics

### Assisted (With AI)

- **True Positives (TP)**: 228 lesions
- **False Positives (FP)**: 48 lesions
- **False Negatives (FN)**: 176 lesions
- **Total Detections**: 276 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.8261 (82.61%)
- **Recall**: 0.5644 (56.44%)
- **F1 Score**: 0.6706 (67.06%)

### Unaided (Without AI)

- **True Positives (TP)**: 228 lesions
- **False Positives (FP)**: 98 lesions
- **False Negatives (FN)**: 176 lesions
- **Total Detections**: 326 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.6994 (69.94%)
- **Recall**: 0.5644 (56.44%)
- **F1 Score**: 0.6247 (62.47%)

## Interpretation

**AI assistance improves lesion-level detection performance.**

- **Precision change**: +0.1267 (+12.67%)
- **Recall change**: +0.0000 (+0.00%)
- **F1 Score change**: +0.0459 (+4.59%)

**Caution**: AI decreases both precision and recall.
