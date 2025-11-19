"""
FR-06: Lesion-level Performance Metrics

병변 단위 성능 지표를 계산합니다 (Secondary analysis).
Patient-level이 primary endpoint인 반면, lesion-level은 AI detection 성능을 평가합니다.

주요 기능:
- Precision (Positive Predictive Value for lesions)
- Recall (Sensitivity for lesions)
- F1 Score (harmonic mean of Precision and Recall)
- Per-reader comparison

Note: mAP (mean Average Precision)는 confidence score가 필요하므로 현재 데이터로는 계산 불가
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import csv

from .logger import setup_logger

logger = setup_logger(__name__)


class LesionMetricsCalculator:
    """
    Lesion-level Performance Metrics

    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    F1 Score = 2 * Precision * Recall / (Precision + Recall)
    """

    def __init__(self):
        """초기화"""
        self.results: Dict = {}
        logger.info("Lesion Metrics Calculator 초기화")

    def calculate_metrics(self,
                         tp: int,
                         fp: int,
                         fn: int) -> Dict[str, float]:
        """
        병변 단위 성능 지표 계산

        Args:
            tp: True Positives (정확히 찾은 병변 수)
            fp: False Positives (잘못 찾은 병변 수)
            fn: False Negatives (놓친 병변 수)

        Returns:
            성능 지표 딕셔너리
        """
        # Precision
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Recall (Sensitivity)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # F1 Score
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        # Additional metrics
        total_detections = tp + fp  # 모델이 찾은 총 병변 수
        total_ground_truth = tp + fn  # 실제 병변 수

        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'total_detections': total_detections,
            'total_ground_truth': total_ground_truth
        }

    def compare_strategies(self,
                          lesion_counts_assisted: Dict[str, int],
                          lesion_counts_unaided: Dict[str, int]) -> Dict:
        """
        Assisted vs Unaided 비교

        Args:
            lesion_counts_assisted: {'TP': ..., 'FP': ..., 'FN': ...}
            lesion_counts_unaided: {'TP': ..., 'FP': ..., 'FN': ...}

        Returns:
            비교 결과 딕셔너리
        """
        logger.info("=" * 80)
        logger.info("Lesion-level Metrics: Assisted vs Unaided")
        logger.info("=" * 80)

        # Assisted 계산
        logger.info("\n[Assisted (With AI)]")
        metrics_assisted = self.calculate_metrics(
            lesion_counts_assisted['TP'],
            lesion_counts_assisted['FP'],
            lesion_counts_assisted['FN']
        )

        logger.info(f"  TP: {metrics_assisted['tp']}, FP: {metrics_assisted['fp']}, FN: {metrics_assisted['fn']}")
        logger.info(f"  Precision: {metrics_assisted['precision']:.4f} ({metrics_assisted['precision']*100:.2f}%)")
        logger.info(f"  Recall:    {metrics_assisted['recall']:.4f} ({metrics_assisted['recall']*100:.2f}%)")
        logger.info(f"  F1 Score:  {metrics_assisted['f1_score']:.4f} ({metrics_assisted['f1_score']*100:.2f}%)")

        # Unaided 계산
        logger.info("\n[Unaided (Without AI)]")
        metrics_unaided = self.calculate_metrics(
            lesion_counts_unaided['TP'],
            lesion_counts_unaided['FP'],
            lesion_counts_unaided['FN']
        )

        logger.info(f"  TP: {metrics_unaided['tp']}, FP: {metrics_unaided['fp']}, FN: {metrics_unaided['fn']}")
        logger.info(f"  Precision: {metrics_unaided['precision']:.4f} ({metrics_unaided['precision']*100:.2f}%)")
        logger.info(f"  Recall:    {metrics_unaided['recall']:.4f} ({metrics_unaided['recall']*100:.2f}%)")
        logger.info(f"  F1 Score:  {metrics_unaided['f1_score']:.4f} ({metrics_unaided['f1_score']*100:.2f}%)")

        # Delta 계산
        logger.info("\n[Δ (Assisted - Unaided)]")
        delta_precision = metrics_assisted['precision'] - metrics_unaided['precision']
        delta_recall = metrics_assisted['recall'] - metrics_unaided['recall']
        delta_f1 = metrics_assisted['f1_score'] - metrics_unaided['f1_score']

        logger.info(f"  Δ Precision: {delta_precision:+.4f} ({delta_precision*100:+.2f}%)")
        logger.info(f"  Δ Recall:    {delta_recall:+.4f} ({delta_recall*100:+.2f}%)")
        logger.info(f"  Δ F1 Score:  {delta_f1:+.4f} ({delta_f1*100:+.2f}%)")

        # 결과 저장
        self.results = {
            'assisted': metrics_assisted,
            'unaided': metrics_unaided,
            'delta': {
                'precision': delta_precision,
                'recall': delta_recall,
                'f1_score': delta_f1
            }
        }

        return self.results

    def create_summary_table(self) -> List[Dict]:
        """
        요약 테이블 생성

        Returns:
            요약 테이블 (리스트 of 딕셔너리)
        """
        if not self.results:
            logger.warning("결과가 없습니다. compare_strategies()를 먼저 실행하세요.")
            return []

        rows = []

        # Assisted
        m_a = self.results['assisted']
        rows.append({
            'Strategy': 'Assisted (With AI)',
            'TP': m_a['tp'],
            'FP': m_a['fp'],
            'FN': m_a['fn'],
            'Precision': f"{m_a['precision']:.4f}",
            'Recall': f"{m_a['recall']:.4f}",
            'F1_Score': f"{m_a['f1_score']:.4f}"
        })

        # Unaided
        m_u = self.results['unaided']
        rows.append({
            'Strategy': 'Unaided (Without AI)',
            'TP': m_u['tp'],
            'FP': m_u['fp'],
            'FN': m_u['fn'],
            'Precision': f"{m_u['precision']:.4f}",
            'Recall': f"{m_u['recall']:.4f}",
            'F1_Score': f"{m_u['f1_score']:.4f}"
        })

        # Delta
        delta = self.results['delta']
        delta_tp = m_a['tp'] - m_u['tp']
        delta_fp = m_a['fp'] - m_u['fp']
        delta_fn = m_a['fn'] - m_u['fn']

        rows.append({
            'Strategy': 'Δ (Assisted - Unaided)',
            'TP': f"{delta_tp:+d}",
            'FP': f"{delta_fp:+d}",
            'FN': f"{delta_fn:+d}",
            'Precision': f"{delta['precision']:+.4f}",
            'Recall': f"{delta['recall']:+.4f}",
            'F1_Score': f"{delta['f1_score']:+.4f}"
        })

        return rows

    def export_results(self, output_dir: Path) -> Dict[str, Path]:
        """
        결과를 파일로 저장

        Args:
            output_dir: 출력 디렉토리

        Returns:
            저장된 파일 경로 딕셔너리
        """
        if not self.results:
            logger.warning("저장할 결과가 없습니다.")
            return {}

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 1. JSON 저장
        json_file = output_dir / "lesion_metrics.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        saved_files['json'] = json_file
        logger.info(f"✓ JSON 저장: {json_file}")

        # 2. CSV 저장
        csv_file = output_dir / "lesion_metrics.csv"
        summary_table = self.create_summary_table()

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if summary_table:
                fieldnames = list(summary_table[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_table)

        saved_files['csv'] = csv_file
        logger.info(f"✓ CSV 저장: {csv_file}")

        # 3. Markdown 리포트
        md_file = output_dir / "lesion_metrics_report.md"
        self._export_markdown_report(md_file)
        saved_files['markdown'] = md_file
        logger.info(f"✓ Markdown 저장: {md_file}")

        return saved_files

    def _export_markdown_report(self, filepath: Path):
        """Markdown 리포트 생성"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Lesion-level Performance Metrics Report\n\n")

            f.write("## Summary Table\n\n")
            f.write("| Strategy | TP | FP | FN | Precision | Recall | F1 Score |\n")
            f.write("|----------|----|----|----|-----------| -------|----------|\n")

            summary_table = self.create_summary_table()
            for row in summary_table:
                f.write(f"| {row['Strategy']} | {row['TP']} | {row['FP']} | {row['FN']} | "
                       f"{row['Precision']} | {row['Recall']} | {row['F1_Score']} |\n")

            f.write("\n")

            # Detailed metrics
            f.write("## Detailed Metrics\n\n")

            # Assisted
            m_a = self.results['assisted']
            f.write("### Assisted (With AI)\n\n")
            f.write(f"- **True Positives (TP)**: {m_a['tp']} lesions\n")
            f.write(f"- **False Positives (FP)**: {m_a['fp']} lesions\n")
            f.write(f"- **False Negatives (FN)**: {m_a['fn']} lesions\n")
            f.write(f"- **Total Detections**: {m_a['total_detections']} lesions\n")
            f.write(f"- **Total Ground Truth**: {m_a['total_ground_truth']} lesions\n\n")
            f.write(f"**Performance:**\n")
            f.write(f"- **Precision**: {m_a['precision']:.4f} ({m_a['precision']*100:.2f}%)\n")
            f.write(f"- **Recall**: {m_a['recall']:.4f} ({m_a['recall']*100:.2f}%)\n")
            f.write(f"- **F1 Score**: {m_a['f1_score']:.4f} ({m_a['f1_score']*100:.2f}%)\n\n")

            # Unaided
            m_u = self.results['unaided']
            f.write("### Unaided (Without AI)\n\n")
            f.write(f"- **True Positives (TP)**: {m_u['tp']} lesions\n")
            f.write(f"- **False Positives (FP)**: {m_u['fp']} lesions\n")
            f.write(f"- **False Negatives (FN)**: {m_u['fn']} lesions\n")
            f.write(f"- **Total Detections**: {m_u['total_detections']} lesions\n")
            f.write(f"- **Total Ground Truth**: {m_u['total_ground_truth']} lesions\n\n")
            f.write(f"**Performance:**\n")
            f.write(f"- **Precision**: {m_u['precision']:.4f} ({m_u['precision']*100:.2f}%)\n")
            f.write(f"- **Recall**: {m_u['recall']:.4f} ({m_u['recall']*100:.2f}%)\n")
            f.write(f"- **F1 Score**: {m_u['f1_score']:.4f} ({m_u['f1_score']*100:.2f}%)\n\n")

            # Interpretation
            f.write("## Interpretation\n\n")

            delta = self.results['delta']

            if delta['f1_score'] > 0:
                f.write(f"**AI assistance improves lesion-level detection performance.**\n\n")
            elif delta['f1_score'] < 0:
                f.write(f"**AI assistance decreases lesion-level detection performance.**\n\n")
            else:
                f.write(f"**AI assistance has no effect on lesion-level detection performance.**\n\n")

            f.write(f"- **Precision change**: {delta['precision']:+.4f} ({delta['precision']*100:+.2f}%)\n")
            f.write(f"- **Recall change**: {delta['recall']:+.4f} ({delta['recall']*100:+.2f}%)\n")
            f.write(f"- **F1 Score change**: {delta['f1_score']:+.4f} ({delta['f1_score']*100:+.2f}%)\n\n")

            # Trade-off analysis
            if delta['precision'] > 0 and delta['recall'] < 0:
                f.write("**Trade-off**: AI increases precision but decreases recall "
                       "(fewer false positives but more false negatives).\n")
            elif delta['precision'] < 0 and delta['recall'] > 0:
                f.write("**Trade-off**: AI decreases precision but increases recall "
                       "(fewer false negatives but more false positives).\n")
            elif delta['precision'] > 0 and delta['recall'] > 0:
                f.write("**Win-win**: AI improves both precision and recall!\n")
            else:
                f.write("**Caution**: AI decreases both precision and recall.\n")
