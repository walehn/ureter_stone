"""
FR-03: Bootstrap Analysis - Patient-level Cluster-robust Resampling

환자 단위(patient_id) resampling으로 bootstrap 신뢰구간 계산.
Reviewer #3의 clustering 무시 문제 해결.

주요 기능:
- Patient-level resampling (B=1000)
- 95% 신뢰구간 계산 (quantile-based)
- Random seed 고정 (재현성)
- Sensitivity, Specificity, PPV, NPV CI

Note: pandas 의존성 제거 - numpy와 순수 Python만 사용
데이터 형식: List[Dict] where each dict has 'patient_id', 'ground_truth', 'prediction'
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from pathlib import Path
import json
import csv

from .logger import setup_logger

logger = setup_logger(__name__)


class BootstrapAnalyzer:
    """
    Patient-level Bootstrap Analysis (pandas-free)

    데이터 형식:
    data = [
        {'patient_id': 'P001', 'ground_truth': 1, 'prediction': 1},
        {'patient_id': 'P002', 'ground_truth': 0, 'prediction': 1},
        ...
    ]
    """

    def __init__(self,
                 n_iterations: int = 1000,
                 confidence_level: float = 0.95,
                 random_seed: Optional[int] = 42):
        """
        Args:
            n_iterations: Bootstrap 반복 횟수 (기본 1000)
            confidence_level: 신뢰수준 (기본 0.95)
            random_seed: 난수 시드 (재현성 보장)
        """
        self.n_iterations = n_iterations
        self.confidence_level = confidence_level
        self.random_seed = random_seed

        # 결과 저장용
        self.bootstrap_results: Dict = {}

        # Random seed 고정
        if random_seed is not None:
            np.random.seed(random_seed)

        logger.info(f"Bootstrap Analyzer 초기화: B={n_iterations}, CI={confidence_level*100}%, seed={random_seed}")

    def resample_patients(self, data: List[Dict]) -> List[Dict]:
        """
        환자 단위로 resampling (with replacement)

        Args:
            data: 레코드 리스트 [{'patient_id': ..., 'ground_truth': ..., 'prediction': ...}, ...]

        Returns:
            리샘플링된 레코드 리스트
        """
        # 환자별로 레코드 그룹화
        patient_records = defaultdict(list)
        for record in data:
            patient_records[record['patient_id']].append(record)

        # 고유 환자 ID 목록
        unique_patients = list(patient_records.keys())
        n_patients = len(unique_patients)

        # 환자 ID를 복원추출로 리샘플링
        resampled_patient_ids = np.random.choice(unique_patients, size=n_patients, replace=True)

        # 각 환자의 모든 레코드를 포함
        resampled_data = []
        for patient_id in resampled_patient_ids:
            resampled_data.extend(patient_records[patient_id])

        return resampled_data

    def aggregate_to_patient_level(self, data: List[Dict]) -> List[Dict]:
        """
        병변 레벨을 환자 레벨로 집계

        환자에 병변이 하나라도 있으면 positive (max aggregation)

        Args:
            data: 레코드 리스트

        Returns:
            환자 레벨 레코드 리스트
        """
        patient_agg = {}

        for record in data:
            patient_id = record['patient_id']

            if patient_id not in patient_agg:
                patient_agg[patient_id] = {
                    'patient_id': patient_id,
                    'ground_truth': record['ground_truth'],
                    'prediction': record['prediction']
                }
            else:
                # Max aggregation (any positive = positive)
                patient_agg[patient_id]['ground_truth'] = max(
                    patient_agg[patient_id]['ground_truth'],
                    record['ground_truth']
                )
                patient_agg[patient_id]['prediction'] = max(
                    patient_agg[patient_id]['prediction'],
                    record['prediction']
                )

        return list(patient_agg.values())

    def calculate_metrics(self, data: List[Dict]) -> Dict[str, float]:
        """
        Confusion matrix로부터 성능 지표 계산

        Args:
            data: 환자 레벨 레코드 리스트

        Returns:
            성능 지표 딕셔너리 (sensitivity, specificity, ppv, npv)
        """
        # Confusion matrix 계산
        tp = sum(1 for r in data if r['ground_truth'] == 1 and r['prediction'] == 1)
        fp = sum(1 for r in data if r['ground_truth'] == 0 and r['prediction'] == 1)
        fn = sum(1 for r in data if r['ground_truth'] == 1 and r['prediction'] == 0)
        tn = sum(1 for r in data if r['ground_truth'] == 0 and r['prediction'] == 0)

        # 성능 지표 계산
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0

        return {
            'sensitivity': sensitivity,
            'specificity': specificity,
            'ppv': ppv,
            'npv': npv
        }

    def bootstrap_single_iteration(self, data: List[Dict]) -> Dict[str, float]:
        """
        Bootstrap 1회 반복 실행

        Args:
            data: 레코드 리스트

        Returns:
            해당 iteration의 성능 지표
        """
        # 1. 환자 단위로 리샘플링
        resampled_data = self.resample_patients(data)

        # 2. 환자 단위로 집계
        patient_level_data = self.aggregate_to_patient_level(resampled_data)

        # 3. 성능 지표 계산
        metrics = self.calculate_metrics(patient_level_data)

        return metrics

    def run_bootstrap(self, data: List[Dict], mode: str = 'assisted') -> Dict:
        """
        전체 Bootstrap 분석 실행 (B회 반복)

        Args:
            data: 레코드 리스트
            mode: 'assisted' 또는 'unaided'

        Returns:
            Bootstrap 결과 딕셔너리
        """
        logger.info(f"Bootstrap 분석 시작: mode={mode}, B={self.n_iterations}")

        # 각 iteration별 결과 저장
        bootstrap_samples = {
            'sensitivity': [],
            'specificity': [],
            'ppv': [],
            'npv': []
        }

        # B회 반복
        for i in range(self.n_iterations):
            if (i + 1) % 100 == 0:
                logger.info(f"  Bootstrap iteration: {i+1}/{self.n_iterations}")

            metrics = self.bootstrap_single_iteration(data)

            # 결과 저장
            for metric_name, value in metrics.items():
                bootstrap_samples[metric_name].append(value)

        # 신뢰구간 계산
        results = self.calculate_confidence_intervals(bootstrap_samples, mode)

        logger.info(f"Bootstrap 분석 완료: {mode}")
        return results

    def calculate_confidence_intervals(self,
                                      bootstrap_samples: Dict[str, List[float]],
                                      mode: str) -> Dict:
        """
        Bootstrap 샘플로부터 신뢰구간 계산 (quantile-based)

        Args:
            bootstrap_samples: 각 metric의 bootstrap 샘플 리스트
            mode: 'assisted' 또는 'unaided'

        Returns:
            신뢰구간 포함 결과 딕셔너리
        """
        alpha = 1 - self.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        results = {
            'mode': mode,
            'n_iterations': self.n_iterations,
            'confidence_level': self.confidence_level,
            'metrics': {}
        }

        for metric_name, samples in bootstrap_samples.items():
            samples_array = np.array(samples)

            # 통계량 계산
            mean = np.mean(samples_array)
            std = np.std(samples_array, ddof=1)
            ci_lower = np.percentile(samples_array, lower_percentile)
            ci_upper = np.percentile(samples_array, upper_percentile)

            results['metrics'][metric_name] = {
                'mean': float(mean),
                'std': float(std),
                'ci_lower': float(ci_lower),
                'ci_upper': float(ci_upper),
                'samples': samples  # 전체 샘플 (visualization용)
            }

            logger.info(f"  {metric_name}: {mean:.3f} (95% CI: {ci_lower:.3f}-{ci_upper:.3f})")

        return results

    def run_comparison(self,
                      data_assisted: List[Dict],
                      data_unaided: List[Dict]) -> Dict:
        """
        Assisted vs Unaided 비교 분석 (각각 bootstrap)

        Args:
            data_assisted: AI 보조 데이터
            data_unaided: AI 미보조 데이터

        Returns:
            비교 결과 딕셔너리
        """
        logger.info("=" * 80)
        logger.info("Bootstrap 비교 분석 시작: Assisted vs Unaided")
        logger.info("=" * 80)

        # 1. Assisted bootstrap
        results_assisted = self.run_bootstrap(data_assisted, mode='assisted')

        # 2. Unaided bootstrap
        results_unaided = self.run_bootstrap(data_unaided, mode='unaided')

        # 3. Delta 계산 (Assisted - Unaided)
        delta_results = self.calculate_delta(results_assisted, results_unaided)

        # 4. 전체 결과 저장
        self.bootstrap_results = {
            'assisted': results_assisted,
            'unaided': results_unaided,
            'delta': delta_results
        }

        return self.bootstrap_results

    def calculate_delta(self, results_assisted: Dict, results_unaided: Dict) -> Dict:
        """
        Assisted - Unaided 차이 계산

        Args:
            results_assisted: Assisted bootstrap 결과
            results_unaided: Unaided bootstrap 결과

        Returns:
            Delta 결과 딕셔너리
        """
        logger.info("\nDelta 계산 (Assisted - Unaided):")

        delta_results = {
            'metrics': {}
        }

        for metric_name in ['sensitivity', 'specificity', 'ppv', 'npv']:
            assisted_samples = np.array(results_assisted['metrics'][metric_name]['samples'])
            unaided_samples = np.array(results_unaided['metrics'][metric_name]['samples'])

            # Delta 계산 (각 iteration별로)
            delta_samples = assisted_samples - unaided_samples

            # 통계량
            mean_delta = np.mean(delta_samples)
            std_delta = np.std(delta_samples, ddof=1)

            alpha = 1 - self.confidence_level
            ci_lower = np.percentile(delta_samples, (alpha / 2) * 100)
            ci_upper = np.percentile(delta_samples, (1 - alpha / 2) * 100)

            # P-value 근사 (CI가 0을 포함하지 않으면 유의)
            p_value_approx = (np.sum(delta_samples <= 0) / len(delta_samples)
                             if mean_delta > 0
                             else np.sum(delta_samples >= 0) / len(delta_samples))

            delta_results['metrics'][metric_name] = {
                'mean': float(mean_delta),
                'std': float(std_delta),
                'ci_lower': float(ci_lower),
                'ci_upper': float(ci_upper),
                'p_value_approx': float(p_value_approx),
                'significant': bool(ci_lower > 0 or ci_upper < 0),  # CI가 0을 포함하지 않으면 유의
                'samples': delta_samples.tolist()
            }

            sig_symbol = "**" if delta_results['metrics'][metric_name]['significant'] else ""
            logger.info(f"  {metric_name}: Δ={mean_delta:+.3f} "
                       f"(95% CI: {ci_lower:+.3f} to {ci_upper:+.3f}) "
                       f"p≈{p_value_approx:.3f} {sig_symbol}")

        return delta_results

    def create_summary_table(self) -> List[Dict]:
        """
        Bootstrap 결과 요약 테이블 생성 (pandas-free)

        Returns:
            요약 테이블 리스트 (각 행은 딕셔너리)
        """
        if not self.bootstrap_results:
            logger.warning("Bootstrap 결과가 없습니다. run_comparison()을 먼저 실행하세요.")
            return []

        rows = []

        for mode in ['unaided', 'assisted']:
            for metric_name in ['sensitivity', 'specificity', 'ppv', 'npv']:
                metric_data = self.bootstrap_results[mode]['metrics'][metric_name]

                rows.append({
                    'Mode': mode.capitalize(),
                    'Metric': metric_name.upper(),
                    'Mean': metric_data['mean'],
                    'Std': metric_data['std'],
                    'CI_Lower': metric_data['ci_lower'],
                    'CI_Upper': metric_data['ci_upper'],
                    'CI_95%': f"[{metric_data['ci_lower']:.3f}, {metric_data['ci_upper']:.3f}]"
                })

        # Delta 추가
        for metric_name in ['sensitivity', 'specificity', 'ppv', 'npv']:
            delta_data = self.bootstrap_results['delta']['metrics'][metric_name]
            sig = " *" if delta_data['significant'] else ""

            rows.append({
                'Mode': 'Delta (A-U)',
                'Metric': metric_name.upper(),
                'Mean': delta_data['mean'],
                'Std': delta_data['std'],
                'CI_Lower': delta_data['ci_lower'],
                'CI_Upper': delta_data['ci_upper'],
                'CI_95%': f"[{delta_data['ci_lower']:+.3f}, {delta_data['ci_upper']:+.3f}]{sig}"
            })

        return rows

    def export_results(self, output_dir: Path) -> Dict[str, Path]:
        """
        Bootstrap 결과를 파일로 저장

        Args:
            output_dir: 출력 디렉토리

        Returns:
            저장된 파일 경로 딕셔너리
        """
        if not self.bootstrap_results:
            logger.warning("저장할 Bootstrap 결과가 없습니다.")
            return {}

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 1. JSON 저장 (전체 결과, samples 포함)
        json_file = output_dir / "bootstrap_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.bootstrap_results, f, indent=2, ensure_ascii=False)
        saved_files['json'] = json_file
        logger.info(f"✓ JSON 저장: {json_file}")

        # 2. CSV 저장 (요약 테이블)
        summary_table = self.create_summary_table()
        csv_file = output_dir / "bootstrap_summary.csv"

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if summary_table:
                fieldnames = list(summary_table[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_table)

        saved_files['csv'] = csv_file
        logger.info(f"✓ CSV 저장: {csv_file}")

        # 3. Markdown 리포트
        md_file = output_dir / "bootstrap_report.md"
        self._export_markdown_report(md_file)
        saved_files['markdown'] = md_file
        logger.info(f"✓ Markdown 저장: {md_file}")

        return saved_files

    def _export_markdown_report(self, filepath: Path):
        """Markdown 리포트 생성"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Bootstrap Analysis Report\n\n")
            f.write(f"**Bootstrap Iterations**: {self.n_iterations}\n")
            f.write(f"**Confidence Level**: {self.confidence_level*100}%\n")
            f.write(f"**Random Seed**: {self.random_seed}\n\n")

            f.write("## Assisted vs Unaided Performance\n\n")

            # 테이블 (수동 생성)
            summary_table = self.create_summary_table()

            # 헤더
            f.write("| Mode | Metric | Mean | Std | CI_Lower | CI_Upper | CI_95% |\n")
            f.write("|------|--------|------|-----|----------|----------|--------|\n")

            # 데이터 행
            for row in summary_table:
                f.write(f"| {row['Mode']} | {row['Metric']} | "
                       f"{row['Mean']:.3f} | {row['Std']:.3f} | "
                       f"{row['CI_Lower']:.3f} | {row['CI_Upper']:.3f} | "
                       f"{row['CI_95%']} |\n")

            f.write("\n\n")

            f.write("## Statistical Significance\n\n")
            f.write("**Significant improvements (95% CI excludes 0):**\n\n")

            for metric_name in ['sensitivity', 'specificity', 'ppv', 'npv']:
                delta_data = self.bootstrap_results['delta']['metrics'][metric_name]
                if delta_data['significant']:
                    f.write(f"- **{metric_name.upper()}**: "
                           f"Δ={delta_data['mean']:+.3f} "
                           f"(95% CI: [{delta_data['ci_lower']:+.3f}, {delta_data['ci_upper']:+.3f}])\n")
