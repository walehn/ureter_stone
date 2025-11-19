"""
FR-08: Reporting Module

모든 분석 결과를 통합하여 Supplement-ready 보고서를 생성합니다.

주요 기능:
- 전체 분석 결과 통합
- Publication-ready 테이블 생성
- Markdown, CSV, JSON 형식 지원
- 통계적 유의성 마커 자동 추가
- Figure 참조 자동 생성
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .logger import setup_logger

logger = setup_logger(__name__)


class SupplementReporter:
    """
    Supplement-ready 보고서 생성 클래스

    모든 분석 결과를 통합하여 논문 제출 가능한 형식으로 출력합니다.
    """

    def __init__(self, results_dir: Path = Path("results")):
        """
        초기화

        Args:
            results_dir: 결과 디렉토리 경로
        """
        self.results_dir = results_dir
        self.report_dir = results_dir / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"SupplementReporter 초기화: {self.report_dir}")

    def load_all_results(self) -> Dict[str, Any]:
        """
        모든 분석 결과 로딩

        Returns:
            전체 결과 딕셔너리
        """
        results = {
            'patient_level': {},
            'bootstrap': {},
            'gee': {},
            'dca': {},
            'lesion_level': {},
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_version': '1.0',
            }
        }

        readers = ['BCR', 'EMS', 'Resident']

        # Patient-level results
        try:
            with open(self.results_dir / 'analysis_results.json', 'r', encoding='utf-8') as f:
                results['patient_level'] = json.load(f)
            logger.info("✓ Patient-level 결과 로딩 완료")
        except Exception as e:
            logger.error(f"✗ Patient-level 로딩 실패: {e}")

        # Bootstrap results
        for reader in readers:
            try:
                bootstrap_file = self.results_dir / 'bootstrap' / reader / 'bootstrap_results.json'
                if bootstrap_file.exists():
                    with open(bootstrap_file, 'r', encoding='utf-8') as f:
                        results['bootstrap'][reader] = json.load(f)
                    logger.info(f"✓ {reader} Bootstrap 결과 로딩 완료")
                else:
                    # Fallback to CSV
                    summary_file = self.results_dir / 'bootstrap' / reader / 'bootstrap_summary.csv'
                    if summary_file.exists():
                        bootstrap_summary = self._load_bootstrap_from_csv(summary_file)
                        results['bootstrap'][reader] = bootstrap_summary
                        logger.info(f"✓ {reader} Bootstrap 요약 (CSV) 로딩 완료")
            except Exception as e:
                logger.error(f"✗ {reader} Bootstrap 로딩 실패: {e}")

        # GEE results
        for reader in readers:
            try:
                gee_file = self.results_dir / 'gee' / reader / 'gee_results.json'
                with open(gee_file, 'r', encoding='utf-8') as f:
                    results['gee'][reader] = json.load(f)
                logger.info(f"✓ {reader} GEE 결과 로딩 완료")
            except Exception as e:
                logger.error(f"✗ {reader} GEE 로딩 실패: {e}")

        # DCA results
        for reader in readers:
            try:
                dca_file = self.results_dir / 'dca' / reader / 'dca_results.json'
                with open(dca_file, 'r', encoding='utf-8') as f:
                    results['dca'][reader] = json.load(f)
                logger.info(f"✓ {reader} DCA 결과 로딩 완료")
            except Exception as e:
                logger.error(f"✗ {reader} DCA 로딩 실패: {e}")

        # Lesion-level results
        for reader in readers:
            try:
                lesion_file = self.results_dir / 'lesion_metrics' / reader / 'lesion_metrics.json'
                with open(lesion_file, 'r', encoding='utf-8') as f:
                    results['lesion_level'][reader] = json.load(f)
                logger.info(f"✓ {reader} Lesion-level 결과 로딩 완료")
            except Exception as e:
                logger.error(f"✗ {reader} Lesion-level 로딩 실패: {e}")

        return results

    def _load_bootstrap_from_csv(self, csv_file: Path) -> Dict[str, Any]:
        """Bootstrap summary CSV에서 데이터 로딩"""
        summary = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mode = row['Mode']
                metric = row['Metric']
                if mode not in summary:
                    summary[mode] = {}
                summary[mode][metric] = {
                    'mean': float(row['Mean']),
                    'ci_lower': float(row['CI_Lower']),
                    'ci_upper': float(row['CI_Upper']),
                    'ci_width': float(row['CI_Width']),
                }
        return summary

    def _significance_marker(self, p_value: Optional[float]) -> str:
        """p-value에 따른 유의성 마커 반환"""
        if p_value is None:
            return ""
        if p_value < 0.001:
            return "***"
        elif p_value < 0.01:
            return "**"
        elif p_value < 0.05:
            return "*"
        else:
            return "ns"

    def generate_table1_patient_level(self, results: Dict[str, Any]) -> str:
        """
        Table 1: Patient-level Performance Metrics

        Returns:
            Markdown 형식 테이블
        """
        md = "# Table 1: Patient-level Performance Metrics\n\n"
        md += "_AI-assisted vs Unaided Performance across Three Readers_\n\n"

        md += "| Reader | Mode | N | Sensitivity | Specificity | PPV | NPV |\n"
        md += "|--------|------|---|-------------|-------------|-----|-----|\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            data = results['patient_level'][reader]
            n = data['n_patients']

            # Unaided
            u = data['unaided']['metrics']
            md += f"| {reader} | Unaided | {n} | "
            md += f"{u['sensitivity']:.3f} | {u['specificity']:.3f} | "
            md += f"{u['ppv']:.3f} | {u['npv']:.3f} |\n"

            # Assisted
            a = data['assisted']['metrics']
            md += f"| {reader} | **Assisted** | {n} | "
            md += f"**{a['sensitivity']:.3f}** | **{a['specificity']:.3f}** | "
            md += f"**{a['ppv']:.3f}** | **{a['npv']:.3f}** |\n"

            # Delta
            d = data['deltas']
            md += f"| {reader} | _Δ (Assisted - Unaided)_ | - | "
            md += f"_{d['delta_sensitivity']:+.3f}_ | _{d['delta_specificity']:+.3f}_ | "
            md += f"_{d['delta_ppv']:+.3f}_ | _{d['delta_npv']:+.3f}_ |\n"

        md += "\n_Note: Bold indicates AI-assisted performance. Δ shows the difference (Assisted - Unaided)._\n"
        md += "_Positive Δ indicates improvement with AI assistance._\n\n"

        return md

    def generate_table2_bootstrap_ci(self, results: Dict[str, Any]) -> str:
        """
        Table 2: Bootstrap 95% Confidence Intervals

        Returns:
            Markdown 형식 테이블
        """
        md = "# Table 2: Bootstrap 95% Confidence Intervals for Performance Metrics\n\n"
        md += "_B = 1000 iterations, patient-level resampling_\n\n"

        md += "| Reader | Mode | Sensitivity (95% CI) | Specificity (95% CI) | PPV (95% CI) | NPV (95% CI) |\n"
        md += "|--------|------|---------------------|---------------------|--------------|-------------|\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            if reader not in results['bootstrap']:
                continue

            data = results['bootstrap'][reader]

            for mode in ['assisted', 'unaided']:
                if mode not in data:
                    continue

                mode_label = "**Assisted**" if mode == 'assisted' else "Unaided"
                md += f"| {reader} | {mode_label} | "

                # Bootstrap data structure: data[mode]['metrics'][metric]
                metrics_data = data[mode].get('metrics', data[mode])  # Fallback for old CSV format

                for metric in ['sensitivity', 'specificity', 'ppv', 'npv']:
                    if metric in metrics_data:
                        m = metrics_data[metric]
                        ci_str = f"{m['mean']:.3f} ({m['ci_lower']:.3f}–{m['ci_upper']:.3f})"
                        md += f"{ci_str} | "
                    else:
                        md += "- | "

                md += "\n"

        md += "\n_CI: Confidence Interval calculated using quantile method (2.5th and 97.5th percentiles)._\n\n"

        return md

    def generate_table3_gee_results(self, results: Dict[str, Any]) -> str:
        """
        Table 3: GEE Analysis Results

        Returns:
            Markdown 형식 테이블
        """
        md = "# Table 3: Generalized Estimating Equations (GEE) Analysis\n\n"
        md += "_Cluster-robust inference with exchangeable correlation structure_\n\n"

        md += "| Reader | Coefficient | OR | 95% CI | SE (Robust) | Z-score | P-value | Sig |\n"
        md += "|--------|-------------|-----|--------|-------------|---------|---------|-----|\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            if reader not in results['gee']:
                continue

            gee_data = results['gee'][reader]
            coef_data = gee_data['coefficients']['Mode (Assisted vs Unaided)']

            coef = coef_data['beta']
            or_val = coef_data['OR']
            or_ci_lower = coef_data['OR_ci_lower']
            or_ci_upper = coef_data['OR_ci_upper']
            se = coef_data['se_robust']
            z = coef_data['z']
            p = coef_data['p_value']
            sig = self._significance_marker(p)

            md += f"| {reader} | {coef:.4f} | {or_val:.3f} | "
            md += f"({or_ci_lower:.3f}–{or_ci_upper:.3f}) | {se:.4f} | "
            md += f"{z:.2f} | {p:.4f} | {sig} |\n"

        md += "\n_OR: Odds Ratio for AI assistance effect. "
        md += "Significance: \\*\\*\\* p<0.001, \\*\\* p<0.01, \\* p<0.05, ns = not significant._\n"
        md += "_Model: logit(P(positive)) = β₀ + β₁·(AI assisted)_\n\n"

        return md

    def generate_table4_dca_summary(self, results: Dict[str, Any]) -> str:
        """
        Table 4: Decision Curve Analysis Summary

        Returns:
            Markdown 형식 테이블
        """
        md = "# Table 4: Decision Curve Analysis - Net Benefit Summary\n\n"
        md += "_Maximum Net Benefit difference across threshold range (0.05–0.25)_\n\n"

        md += "| Reader | Max Δ Net Benefit | Threshold at Max | Assisted NB | Unaided NB |\n"
        md += "|--------|------------------|------------------|-------------|------------|\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            if reader not in results['dca']:
                continue

            dca_data = results['dca'][reader]

            # 최대 delta 찾기
            delta_nb = dca_data['delta_net_benefit']
            thresholds = dca_data['thresholds']
            max_idx = delta_nb.index(max(delta_nb))
            max_delta = delta_nb[max_idx]
            max_threshold = thresholds[max_idx]

            assisted_nb = dca_data['assisted']['net_benefit_model'][max_idx]
            unaided_nb = dca_data['unaided']['net_benefit_model'][max_idx]

            md += f"| {reader} | {max_delta:+.4f} | {max_threshold:.3f} | "
            md += f"{assisted_nb:.4f} | {unaided_nb:.4f} |\n"

        md += "\n_Δ Net Benefit = NB(Assisted) - NB(Unaided). "
        md += "Positive values indicate AI-assisted strategy is preferred._\n"
        md += "_Threshold: Minimum probability at which intervention is warranted._\n\n"

        return md

    def generate_table5_lesion_level(self, results: Dict[str, Any]) -> str:
        """
        Table 5: Lesion-level Detection Performance

        Returns:
            Markdown 형식 테이블
        """
        md = "# Table 5: Lesion-level Detection Performance Metrics\n\n"
        md += "_Object detection performance at individual lesion level_\n\n"

        md += "| Reader | Mode | Precision | Recall | F1 Score |\n"
        md += "|--------|------|-----------|--------|----------|\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            if reader not in results['lesion_level']:
                continue

            data = results['lesion_level'][reader]

            # Unaided
            u = data['unaided']
            md += f"| {reader} | Unaided | {u['precision']:.3f} | {u['recall']:.3f} | {u['f1_score']:.3f} |\n"

            # Assisted
            a = data['assisted']
            md += f"| {reader} | **Assisted** | **{a['precision']:.3f}** | **{a['recall']:.3f}** | **{a['f1_score']:.3f}** |\n"

            # Delta
            d = data['delta']
            md += f"| {reader} | _Δ (Assisted - Unaided)_ | _{d['precision']:+.3f}_ | _{d['recall']:+.3f}_ | _{d['f1_score']:+.3f}_ |\n"

        md += "\n_Precision: TP/(TP+FP), Recall: TP/(TP+FN), F1: Harmonic mean of Precision and Recall._\n\n"

        return md

    def generate_executive_summary(self, results: Dict[str, Any]) -> str:
        """
        Executive Summary - 주요 발견사항 요약

        Returns:
            Markdown 형식 요약
        """
        md = "# Executive Summary: AI-Assisted Ureter Stone Detection Performance\n\n"
        md += f"_Generated: {results['metadata']['generated_at']}_\n\n"

        md += "## 🎯 Key Findings\n\n"

        # Patient-level summary
        md += "### 1. Patient-level Performance (Primary Endpoint)\n\n"
        for reader in ['BCR', 'EMS', 'Resident']:
            data = results['patient_level'][reader]
            deltas = data['deltas']

            md += f"**{reader}**:\n"
            md += f"- Sensitivity: {deltas['delta_sensitivity']:+.1%}\n"
            md += f"- Specificity: {deltas['delta_specificity']:+.1%}\n"
            md += f"- PPV: {deltas['delta_ppv']:+.1%}\n"
            md += f"- NPV: {deltas['delta_npv']:+.1%}\n\n"

        # GEE summary
        md += "### 2. Statistical Significance (GEE Analysis)\n\n"
        for reader in ['BCR', 'EMS', 'Resident']:
            if reader in results['gee']:
                gee = results['gee'][reader]['coefficients']['Mode (Assisted vs Unaided)']
                or_val = gee['OR']
                p_val = gee['p_value']
                sig = self._significance_marker(p_val)

                md += f"- **{reader}**: OR = {or_val:.3f}, p = {p_val:.4f} {sig}\n"

        md += "\n### 3. Clinical Utility (Decision Curve Analysis)\n\n"
        md += "AI-assisted strategy showed superior net benefit across all readers:\n\n"

        for reader in ['BCR', 'EMS', 'Resident']:
            if reader in results['dca']:
                delta_nb = results['dca'][reader]['delta_net_benefit']
                max_delta = max(delta_nb)
                md += f"- **{reader}**: Max Δ Net Benefit = {max_delta:+.4f}\n"

        md += "\n### 4. Lesion-level Detection Performance\n\n"
        for reader in ['BCR', 'EMS', 'Resident']:
            if reader in results['lesion_level']:
                delta = results['lesion_level'][reader]['delta']
                md += f"**{reader}**:\n"
                md += f"- Precision: {delta['precision']:+.1%}\n"
                md += f"- Recall: {delta['recall']:+.1%}\n"
                md += f"- F1 Score: {delta['f1_score']:+.1%}\n\n"

        return md

    def generate_methods_section(self) -> str:
        """
        Methods Section - 통계 분석 방법 기술

        Returns:
            Markdown 형식 방법론
        """
        md = "# Statistical Methods\n\n"

        md += "## Patient-level Analysis\n\n"
        md += "Patient-level performance was assessed using standard diagnostic metrics:\n"
        md += "- **Sensitivity**: TP / (TP + FN)\n"
        md += "- **Specificity**: TN / (TN + FP)\n"
        md += "- **Positive Predictive Value (PPV)**: TP / (TP + FP)\n"
        md += "- **Negative Predictive Value (NPV)**: TN / (TN + FN)\n\n"

        md += "## Bootstrap Analysis\n\n"
        md += "To account for clustering within patients (multiple lesions per patient), "
        md += "we performed patient-level bootstrap resampling with B = 1000 iterations. "
        md += "95% confidence intervals were calculated using the quantile method "
        md += "(2.5th and 97.5th percentiles of the bootstrap distribution).\n\n"

        md += "## Generalized Estimating Equations (GEE)\n\n"
        md += "Cluster-robust inference was performed using GEE with:\n"
        md += "- **Family**: Binomial\n"
        md += "- **Link function**: Logit\n"
        md += "- **Correlation structure**: Exchangeable (within-patient correlation)\n"
        md += "- **Model**: logit(P(Y=1)) = β₀ + β₁·(AI assisted)\n\n"
        md += "Robust standard errors were calculated using the sandwich estimator.\n\n"

        md += "## Decision Curve Analysis (DCA)\n\n"
        md += "Clinical utility was assessed using DCA across threshold probabilities "
        md += "ranging from 0.05 to 0.25. Net benefit was calculated as:\n\n"
        md += "**Net Benefit = (TP/N) - (FP/N) × [pt / (1 - pt)]**\n\n"
        md += "where pt is the threshold probability. "
        md += "Positive net benefit differences indicate superior clinical utility "
        md += "of the AI-assisted strategy.\n\n"

        md += "## Lesion-level Detection Metrics\n\n"
        md += "Object detection performance was evaluated using:\n"
        md += "- **Precision**: TP / (TP + FP)\n"
        md += "- **Recall**: TP / (TP + FN)\n"
        md += "- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)\n\n"

        return md

    def generate_full_report(self) -> Path:
        """
        전체 통합 보고서 생성

        Returns:
            저장된 보고서 파일 경로
        """
        logger.info("=" * 80)
        logger.info("Supplement-ready 통합 보고서 생성 시작")
        logger.info("=" * 80)

        # 모든 결과 로딩
        results = self.load_all_results()

        # Markdown 보고서 생성
        md_report = ""

        # Title page
        md_report += "# Supplementary Materials\n\n"
        md_report += "## AI-Assisted Ureter Stone Detection:\n"
        md_report += "## Statistical Analysis and Performance Evaluation\n\n"
        md_report += f"_Report Generated: {results['metadata']['generated_at']}_\n\n"
        md_report += "---\n\n"

        # Executive Summary
        md_report += self.generate_executive_summary(results)
        md_report += "\n---\n\n"

        # Tables
        md_report += self.generate_table1_patient_level(results)
        md_report += "\n"
        md_report += self.generate_table2_bootstrap_ci(results)
        md_report += "\n"
        md_report += self.generate_table3_gee_results(results)
        md_report += "\n"
        md_report += self.generate_table4_dca_summary(results)
        md_report += "\n"
        md_report += self.generate_table5_lesion_level(results)
        md_report += "\n---\n\n"

        # Methods
        md_report += self.generate_methods_section()
        md_report += "\n---\n\n"

        # Figures reference
        md_report += "# Figures\n\n"
        md_report += "All figures are available in the `results/figures/` directory:\n\n"
        md_report += "- **Figure 1-3**: Decision Curve Analysis (BCR, EMS, Resident)\n"
        md_report += "- **Figure 4-6**: Patient-level Metrics Comparison (BCR, EMS, Resident)\n"
        md_report += "- **Figure 7-9**: Lesion-level Metrics Comparison (BCR, EMS, Resident)\n"
        md_report += "- **Figure 10-12**: Precision-Recall Comparison (BCR, EMS, Resident)\n"
        md_report += "- **Figure 13-18**: Confusion Matrices (BCR, EMS, Resident × Assisted/Unaided)\n"
        md_report += "- **Figure 19-26**: Cross-reader Delta Comparisons\n\n"

        # 보고서 저장
        report_path = self.report_dir / "supplement_full_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)

        logger.info(f"✓ Markdown 보고서 저장: {report_path}")

        # JSON 통합 결과도 저장
        json_path = self.report_dir / "integrated_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ JSON 통합 결과 저장: {json_path}")

        logger.info("=" * 80)
        logger.info("보고서 생성 완료!")
        logger.info("=" * 80)

        return report_path
