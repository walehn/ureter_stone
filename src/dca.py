"""
FR-05: Decision Curve Analysis (DCA)

임상 의사결정의 유용성(clinical utility)을 평가합니다.
Net benefit을 통해 AI 보조 진단의 실제 임상적 가치를 정량화합니다.

주요 기능:
- Net Benefit 계산 (Vickers & Elkin, 2006)
- Threshold probability 범위에서 비교
- Treat all, Treat none, Prediction model 비교
- Clinical utility 평가

References:
- Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating
  prediction models. Med Decis Making. 2006;26(6):565-74.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import csv

from .logger import setup_logger

logger = setup_logger(__name__)


class DecisionCurveAnalyzer:
    """
    Decision Curve Analysis

    Net Benefit = (TP/N) - (FP/N) × (pt/(1-pt))

    where:
    - TP/N: True Positive rate (benefit of treatment)
    - FP/N: False Positive rate (harm of unnecessary treatment)
    - pt: threshold probability
    - pt/(1-pt): harm-to-benefit ratio
    """

    def __init__(self,
                 threshold_min: float = 0.05,
                 threshold_max: float = 0.25,
                 n_thresholds: int = 50):
        """
        Args:
            threshold_min: 최소 threshold probability
            threshold_max: 최대 threshold probability
            n_thresholds: threshold 개수
        """
        self.threshold_min = threshold_min
        self.threshold_max = threshold_max
        self.n_thresholds = n_thresholds

        # Threshold probability 범위
        self.thresholds = np.linspace(threshold_min, threshold_max, n_thresholds)

        # 결과 저장
        self.results: Dict = {}

        logger.info(f"DCA Analyzer 초기화: threshold range=[{threshold_min}, {threshold_max}], n={n_thresholds}")

    def calculate_net_benefit(self,
                             tp: int,
                             fp: int,
                             fn: int,
                             tn: int,
                             threshold: float) -> float:
        """
        Net Benefit 계산

        Net Benefit = (TP/N) - (FP/N) × (threshold/(1-threshold))

        Args:
            tp, fp, fn, tn: Confusion matrix
            threshold: threshold probability

        Returns:
            net_benefit: Net benefit at given threshold
        """
        n = tp + fp + fn + tn

        if n == 0:
            return 0.0

        # TP rate
        tp_rate = tp / n

        # FP rate
        fp_rate = fp / n

        # Harm-to-benefit ratio
        harm_benefit_ratio = threshold / (1 - threshold) if threshold < 1.0 else 0.0

        # Net Benefit
        net_benefit = tp_rate - fp_rate * harm_benefit_ratio

        return net_benefit

    def treat_all_net_benefit(self,
                             prevalence: float,
                             threshold: float) -> float:
        """
        Treat all 전략의 Net Benefit

        모든 환자를 양성으로 판단 (치료)
        Net Benefit = Prevalence - (1 - Prevalence) × (threshold/(1-threshold))

        Args:
            prevalence: 질병 유병률
            threshold: threshold probability

        Returns:
            net_benefit: Net benefit for treat all strategy
        """
        harm_benefit_ratio = threshold / (1 - threshold) if threshold < 1.0 else 0.0
        net_benefit = prevalence - (1 - prevalence) * harm_benefit_ratio

        return net_benefit

    def treat_none_net_benefit(self) -> float:
        """
        Treat none 전략의 Net Benefit

        아무도 치료하지 않음 → Net Benefit = 0

        Returns:
            0.0
        """
        return 0.0

    def analyze_strategy(self,
                        confusion_matrix: Dict[str, int],
                        strategy_name: str = "Model") -> Dict:
        """
        하나의 전략(모델)에 대한 DCA 수행

        Args:
            confusion_matrix: {'TP': ..., 'FP': ..., 'FN': ..., 'TN': ...}
            strategy_name: 전략 이름

        Returns:
            DCA 결과 딕셔너리
        """
        tp = confusion_matrix['TP']
        fp = confusion_matrix['FP']
        fn = confusion_matrix['FN']
        tn = confusion_matrix['TN']

        n = tp + fp + fn + tn
        prevalence = (tp + fn) / n if n > 0 else 0.0

        # 각 threshold에서 net benefit 계산
        net_benefits_model = []
        net_benefits_all = []
        net_benefits_none = []

        for threshold in self.thresholds:
            # Model
            nb_model = self.calculate_net_benefit(tp, fp, fn, tn, threshold)
            net_benefits_model.append(nb_model)

            # Treat all
            nb_all = self.treat_all_net_benefit(prevalence, threshold)
            net_benefits_all.append(nb_all)

            # Treat none
            nb_none = self.treat_none_net_benefit()
            net_benefits_none.append(nb_none)

        results = {
            'strategy_name': strategy_name,
            'prevalence': prevalence,
            'n': n,
            'confusion_matrix': confusion_matrix,
            'thresholds': self.thresholds.tolist(),
            'net_benefit_model': net_benefits_model,
            'net_benefit_treat_all': net_benefits_all,
            'net_benefit_treat_none': net_benefits_none
        }

        logger.info(f"\n[{strategy_name}] DCA 분석 완료:")
        logger.info(f"  Prevalence: {prevalence:.3f}")
        logger.info(f"  N: {n}")
        logger.info(f"  Max Net Benefit (Model): {max(net_benefits_model):.4f} at threshold={self.thresholds[np.argmax(net_benefits_model)]:.3f}")

        return results

    def compare_strategies(self,
                          cm_assisted: Dict[str, int],
                          cm_unaided: Dict[str, int]) -> Dict:
        """
        Assisted vs Unaided 전략 비교

        Args:
            cm_assisted: Assisted confusion matrix
            cm_unaided: Unaided confusion matrix

        Returns:
            비교 결과 딕셔너리
        """
        logger.info("=" * 80)
        logger.info("Decision Curve Analysis: Assisted vs Unaided")
        logger.info("=" * 80)

        # Assisted 분석
        results_assisted = self.analyze_strategy(cm_assisted, "Assisted (With AI)")

        # Unaided 분석
        results_unaided = self.analyze_strategy(cm_unaided, "Unaided (Without AI)")

        # Delta Net Benefit 계산
        delta_nb = []
        for i in range(len(self.thresholds)):
            delta = results_assisted['net_benefit_model'][i] - results_unaided['net_benefit_model'][i]
            delta_nb.append(delta)

        # 전체 결과
        self.results = {
            'assisted': results_assisted,
            'unaided': results_unaided,
            'delta_net_benefit': delta_nb,
            'thresholds': self.thresholds.tolist()
        }

        # 요약 통계
        logger.info("\n" + "=" * 80)
        logger.info("비교 요약")
        logger.info("=" * 80)

        max_delta_idx = np.argmax(np.abs(delta_nb))
        max_delta = delta_nb[max_delta_idx]
        max_delta_threshold = self.thresholds[max_delta_idx]

        logger.info(f"\nMaximum difference in Net Benefit:")
        logger.info(f"  Δ Net Benefit: {max_delta:+.4f} at threshold={max_delta_threshold:.3f}")
        logger.info(f"  Assisted: {results_assisted['net_benefit_model'][max_delta_idx]:.4f}")
        logger.info(f"  Unaided:  {results_unaided['net_benefit_model'][max_delta_idx]:.4f}")

        # AI가 더 나은 threshold 범위 찾기
        better_indices = [i for i, d in enumerate(delta_nb) if d > 0]
        if better_indices:
            better_thresholds = self.thresholds[better_indices]
            logger.info(f"\nAI is better at threshold range: [{better_thresholds[0]:.3f}, {better_thresholds[-1]:.3f}]")
            logger.info(f"  ({len(better_indices)}/{len(delta_nb)} thresholds, {len(better_indices)/len(delta_nb)*100:.1f}%)")
        else:
            logger.info("\nAI is not better at any threshold in the analyzed range.")

        return self.results

    def create_summary_table(self) -> List[Dict]:
        """
        DCA 결과 요약 테이블 생성

        Returns:
            요약 테이블 (리스트 of 딕셔너리)
        """
        if not self.results:
            logger.warning("DCA 결과가 없습니다. compare_strategies()를 먼저 실행하세요.")
            return []

        rows = []

        # 주요 threshold만 선택 (0.05, 0.10, 0.15, 0.20, 0.25)
        key_thresholds = [0.05, 0.10, 0.15, 0.20, 0.25]

        for target_threshold in key_thresholds:
            # 가장 가까운 threshold 찾기
            idx = np.argmin(np.abs(self.thresholds - target_threshold))
            threshold = self.thresholds[idx]

            nb_assisted = self.results['assisted']['net_benefit_model'][idx]
            nb_unaided = self.results['unaided']['net_benefit_model'][idx]
            nb_all = self.results['assisted']['net_benefit_treat_all'][idx]
            nb_none = 0.0
            delta = self.results['delta_net_benefit'][idx]

            rows.append({
                'Threshold': f"{threshold:.2f}",
                'NB_Assisted': f"{nb_assisted:.4f}",
                'NB_Unaided': f"{nb_unaided:.4f}",
                'NB_Treat_All': f"{nb_all:.4f}",
                'NB_Treat_None': f"{nb_none:.4f}",
                'Delta_NB': f"{delta:+.4f}",
                'Better_Strategy': 'Assisted' if delta > 0 else 'Unaided' if delta < 0 else 'Equal'
            })

        return rows

    def export_results(self, output_dir: Path) -> Dict[str, Path]:
        """
        DCA 결과를 파일로 저장

        Args:
            output_dir: 출력 디렉토리

        Returns:
            저장된 파일 경로 딕셔너리
        """
        if not self.results:
            logger.warning("저장할 DCA 결과가 없습니다.")
            return {}

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 1. JSON 저장
        json_file = output_dir / "dca_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        saved_files['json'] = json_file
        logger.info(f"✓ JSON 저장: {json_file}")

        # 2. CSV 저장 (전체 curve 데이터)
        csv_file = output_dir / "dca_curve.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Threshold', 'NB_Assisted', 'NB_Unaided', 'NB_Treat_All',
                         'NB_Treat_None', 'Delta_NB']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i, threshold in enumerate(self.thresholds):
                writer.writerow({
                    'Threshold': f"{threshold:.4f}",
                    'NB_Assisted': f"{self.results['assisted']['net_benefit_model'][i]:.6f}",
                    'NB_Unaided': f"{self.results['unaided']['net_benefit_model'][i]:.6f}",
                    'NB_Treat_All': f"{self.results['assisted']['net_benefit_treat_all'][i]:.6f}",
                    'NB_Treat_None': f"{0.0:.6f}",
                    'Delta_NB': f"{self.results['delta_net_benefit'][i]:+.6f}"
                })

        saved_files['csv'] = csv_file
        logger.info(f"✓ CSV 저장: {csv_file}")

        # 3. Summary CSV
        summary_csv = output_dir / "dca_summary.csv"
        summary_table = self.create_summary_table()

        with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
            if summary_table:
                fieldnames = list(summary_table[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_table)

        saved_files['summary_csv'] = summary_csv
        logger.info(f"✓ Summary CSV 저장: {summary_csv}")

        # 4. Markdown 리포트
        md_file = output_dir / "dca_report.md"
        self._export_markdown_report(md_file)
        saved_files['markdown'] = md_file
        logger.info(f"✓ Markdown 저장: {md_file}")

        return saved_files

    def _export_markdown_report(self, filepath: Path):
        """Markdown 리포트 생성"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Decision Curve Analysis Report\n\n")

            # Model info
            f.write("## Analysis Settings\n\n")
            f.write(f"- **Threshold Range**: [{self.threshold_min}, {self.threshold_max}]\n")
            f.write(f"- **Number of Thresholds**: {self.n_thresholds}\n\n")

            # Sample info
            f.write("## Sample Information\n\n")
            f.write(f"### Assisted (With AI)\n")
            f.write(f"- **N**: {self.results['assisted']['n']}\n")
            f.write(f"- **Prevalence**: {self.results['assisted']['prevalence']:.3f}\n")
            cm_a = self.results['assisted']['confusion_matrix']
            f.write(f"- **Confusion Matrix**: TP={cm_a['TP']}, FP={cm_a['FP']}, FN={cm_a['FN']}, TN={cm_a['TN']}\n\n")

            f.write(f"### Unaided (Without AI)\n")
            f.write(f"- **N**: {self.results['unaided']['n']}\n")
            f.write(f"- **Prevalence**: {self.results['unaided']['prevalence']:.3f}\n")
            cm_u = self.results['unaided']['confusion_matrix']
            f.write(f"- **Confusion Matrix**: TP={cm_u['TP']}, FP={cm_u['FP']}, FN={cm_u['FN']}, TN={cm_u['TN']}\n\n")

            # Summary table
            f.write("## Net Benefit Summary\n\n")
            f.write("| Threshold | NB (Assisted) | NB (Unaided) | NB (Treat All) | Delta NB | Better Strategy |\n")
            f.write("|-----------|---------------|--------------|----------------|----------|------------------|\n")

            summary_table = self.create_summary_table()
            for row in summary_table:
                f.write(f"| {row['Threshold']} | {row['NB_Assisted']} | {row['NB_Unaided']} | "
                       f"{row['NB_Treat_All']} | {row['Delta_NB']} | {row['Better_Strategy']} |\n")

            f.write("\n")

            # Clinical interpretation
            f.write("## Clinical Interpretation\n\n")

            delta_nb = self.results['delta_net_benefit']
            positive_count = sum(1 for d in delta_nb if d > 0)
            positive_pct = positive_count / len(delta_nb) * 100

            if positive_pct > 50:
                f.write(f"**AI assistance provides clinical benefit** across most threshold probabilities "
                       f"({positive_pct:.1f}% of analyzed range).\n\n")
            elif positive_pct > 0:
                f.write(f"**AI assistance provides clinical benefit** at some threshold probabilities "
                       f"({positive_pct:.1f}% of analyzed range).\n\n")
            else:
                f.write(f"**AI assistance does not provide clinical benefit** in the analyzed threshold range.\n\n")

            max_delta_idx = np.argmax(np.abs(delta_nb))
            max_delta = delta_nb[max_delta_idx]
            max_threshold = self.thresholds[max_delta_idx]

            f.write(f"**Maximum difference**: Δ Net Benefit = {max_delta:+.4f} at threshold = {max_threshold:.3f}\n")
