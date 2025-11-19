# Lesion-level Performance Metrics Report

## Summary Table

| Strategy | TP | FP | FN | Precision | Recall | F1 Score |
|----------|----|----|----|-----------| -------|----------|
| Assisted (With AI) | 230 | 72 | 174 | 0.7616 | 0.5693 | 0.6516 |
| Unaided (Without AI) | 204 | 262 | 200 | 0.4378 | 0.5050 | 0.4690 |
| Δ (Assisted - Unaided) | +26 | -190 | -26 | +0.3238 | +0.0644 | +0.1826 |

## Detailed Metrics

### Assisted (With AI)

- **True Positives (TP)**: 230 lesions
- **False Positives (FP)**: 72 lesions
- **False Negatives (FN)**: 174 lesions
- **Total Detections**: 302 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.7616 (76.16%)
- **Recall**: 0.5693 (56.93%)
- **F1 Score**: 0.6516 (65.16%)

### Unaided (Without AI)

- **True Positives (TP)**: 204 lesions
- **False Positives (FP)**: 262 lesions
- **False Negatives (FN)**: 200 lesions
- **Total Detections**: 466 lesions
- **Total Ground Truth**: 404 lesions

**Performance:**
- **Precision**: 0.4378 (43.78%)
- **Recall**: 0.5050 (50.50%)
- **F1 Score**: 0.4690 (46.90%)

## Interpretation

**AI assistance improves lesion-level detection performance.**

- **Precision change**: +0.3238 (+32.38%)
- **Recall change**: +0.0644 (+6.44%)
- **F1 Score change**: +0.1826 (+18.26%)

**Win-win**: AI improves both precision and recall!
