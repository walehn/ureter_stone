"""
FR-04: GEE (Generalized Estimating Equations) Analysis

Cluster-robust inference for correlated data (환자 내 병변 간 상관관계 고려).
Reviewer #3의 clustering 문제 해결을 위한 두 번째 접근법 (Bootstrap과 함께 사용).

주요 기능:
- Binomial family, Logit link
- Exchangeable correlation structure
- Robust sandwich standard errors
- Wald test for coefficients

Note: statsmodels 의존성 제거 - numpy/scipy 직접 구현
"""

import numpy as np
from scipy import optimize
from scipy.special import expit  # logistic sigmoid
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from pathlib import Path
import json
import csv

from .logger import setup_logger

logger = setup_logger(__name__)


class GEEAnalyzer:
    """
    Generalized Estimating Equations (간소화 구현)

    Family: Binomial
    Link: Logit
    Correlation: Exchangeable (within-patient)

    데이터 형식:
    data = [
        {'patient_id': 'P001', 'outcome': 1, 'mode': 1, 'reader_id': 0},  # mode: 1=assisted, 0=unaided
        ...
    ]
    """

    def __init__(self, max_iter: int = 100, tol: float = 1e-6):
        """
        Args:
            max_iter: 최대 반복 횟수
            tol: 수렴 허용 오차
        """
        self.max_iter = max_iter
        self.tol = tol

        # 결과 저장
        self.results: Dict = {}
        self.coefficients: Optional[np.ndarray] = None
        self.robust_se: Optional[np.ndarray] = None
        self.covariance_matrix: Optional[np.ndarray] = None

        logger.info(f"GEE Analyzer 초기화: max_iter={max_iter}, tol={tol}")

    def prepare_data(self, data: List[Dict],
                    include_reader: bool = False) -> Tuple[np.ndarray, np.ndarray, List, np.ndarray]:
        """
        데이터를 GEE 분석용 행렬로 변환

        Args:
            data: 레코드 리스트
            include_reader: reader_id를 공변량으로 포함할지 여부

        Returns:
            y: outcome vector (n,)
            X: design matrix (n, p)
            cluster_ids: 클러스터(환자) ID 리스트
            cluster_sizes: 각 클러스터의 크기
        """
        # 환자별로 데이터 그룹화
        clusters = defaultdict(list)
        for record in data:
            clusters[record['patient_id']].append(record)

        cluster_ids = []
        cluster_sizes = []
        y_list = []
        X_list = []

        for patient_id, records in clusters.items():
            n_obs = len(records)
            cluster_sizes.append(n_obs)

            for record in records:
                cluster_ids.append(patient_id)
                y_list.append(record['outcome'])

                # Design matrix: [intercept, mode, reader_id (optional)]
                if include_reader:
                    X_list.append([1, record['mode'], record.get('reader_id', 0)])
                else:
                    X_list.append([1, record['mode']])

        y = np.array(y_list)
        X = np.array(X_list)
        cluster_sizes = np.array(cluster_sizes)

        logger.info(f"데이터 준비 완료: n={len(y)}, p={X.shape[1]}, clusters={len(clusters)}")
        logger.info(f"  Mean cluster size: {np.mean(cluster_sizes):.1f} (range: {np.min(cluster_sizes)}-{np.max(cluster_sizes)})")

        return y, X, cluster_ids, cluster_sizes

    def logistic_regression(self, y: np.ndarray, X: np.ndarray) -> np.ndarray:
        """
        Logistic regression (MLE)

        Args:
            y: outcome vector
            X: design matrix

        Returns:
            beta: coefficient estimates
        """
        def neg_log_likelihood(beta):
            """Negative log-likelihood"""
            mu = expit(X @ beta)
            # Numerical stability
            mu = np.clip(mu, 1e-10, 1 - 1e-10)
            return -np.sum(y * np.log(mu) + (1 - y) * np.log(1 - mu))

        # 초기값: 모두 0
        beta_init = np.zeros(X.shape[1])

        # 최적화
        result = optimize.minimize(
            neg_log_likelihood,
            beta_init,
            method='BFGS',
            options={'maxiter': self.max_iter}
        )

        if not result.success:
            logger.warning(f"Logistic regression 수렴 실패: {result.message}")

        return result.x

    def compute_working_correlation(self,
                                    y: np.ndarray,
                                    mu: np.ndarray,
                                    cluster_ids: List,
                                    correlation_structure: str = 'exchangeable') -> float:
        """
        Working correlation 추정 (Exchangeable structure)

        Args:
            y: outcome vector
            mu: predicted probabilities
            cluster_ids: 클러스터 ID 리스트
            correlation_structure: 'exchangeable' (모든 쌍이 동일한 상관관계)

        Returns:
            alpha: correlation parameter
        """
        if correlation_structure != 'exchangeable':
            raise NotImplementedError("Only exchangeable correlation is implemented")

        # Residuals
        residuals = y - mu

        # Cluster별로 그룹화
        clusters = defaultdict(list)
        residuals_dict = defaultdict(list)

        for i, cluster_id in enumerate(cluster_ids):
            clusters[cluster_id].append(i)
            residuals_dict[cluster_id].append(residuals[i])

        # Within-cluster correlations 계산
        correlations = []

        for cluster_id, indices in clusters.items():
            if len(indices) < 2:
                continue

            r = residuals[indices]
            # Pairwise products
            for i in range(len(r)):
                for j in range(i + 1, len(r)):
                    correlations.append(r[i] * r[j])

        if len(correlations) == 0:
            return 0.0

        alpha = np.mean(correlations)
        alpha = np.clip(alpha, -0.99, 0.99)  # 수치 안정성

        logger.info(f"  Working correlation (exchangeable): α={alpha:.3f}")

        return alpha

    def sandwich_variance(self,
                         X: np.ndarray,
                         y: np.ndarray,
                         mu: np.ndarray,
                         cluster_ids: List,
                         alpha: float = 0.0) -> np.ndarray:
        """
        Sandwich (robust) variance estimator

        V_robust = A^(-1) * B * A^(-1)

        where:
        - A = X'WX (model-based variance)
        - B = Σ X_i' (Y_i - μ_i)(Y_i - μ_i)' X_i (empirical variance)

        Args:
            X: design matrix
            y: outcome vector
            mu: predicted probabilities
            cluster_ids: 클러스터 ID 리스트
            alpha: correlation parameter

        Returns:
            V_robust: robust covariance matrix
        """
        n, p = X.shape

        # Weights (diagonal elements of working variance)
        # Var(Y_i) = μ_i(1 - μ_i)
        w = mu * (1 - mu)
        w = np.clip(w, 1e-10, None)  # 수치 안정성
        W = np.diag(w)

        # A = X'WX (model-based information)
        A = X.T @ W @ X

        # B = empirical variance (cluster-robust)
        clusters = defaultdict(list)
        for i, cluster_id in enumerate(cluster_ids):
            clusters[cluster_id].append(i)

        B = np.zeros((p, p))

        for cluster_id, indices in clusters.items():
            X_i = X[indices]
            y_i = y[indices]
            mu_i = mu[indices]

            # Residuals
            r_i = y_i - mu_i

            # Contribution to B
            # X_i' * r_i * r_i' * X_i
            score_i = X_i.T @ r_i
            B += np.outer(score_i, score_i)

        # Robust variance: A^(-1) * B * A^(-1)
        try:
            A_inv = np.linalg.inv(A)
            V_robust = A_inv @ B @ A_inv
        except np.linalg.LinAlgError:
            logger.warning("A 행렬이 특이행렬입니다. Pseudoinverse 사용")
            A_inv = np.linalg.pinv(A)
            V_robust = A_inv @ B @ A_inv

        return V_robust

    def fit(self, data: List[Dict], include_reader: bool = False) -> Dict:
        """
        GEE 모델 적합

        Args:
            data: 레코드 리스트
            include_reader: reader_id 포함 여부

        Returns:
            결과 딕셔너리
        """
        logger.info("=" * 80)
        logger.info("GEE 분석 시작")
        logger.info("=" * 80)

        # 1. 데이터 준비
        y, X, cluster_ids, cluster_sizes = self.prepare_data(data, include_reader)

        # 2. Logistic regression (초기 추정)
        logger.info("\n[Step 1] Logistic Regression (초기 추정)...")
        beta = self.logistic_regression(y, X)

        # 3. Predicted probabilities
        mu = expit(X @ beta)

        # 4. Working correlation 추정
        logger.info("\n[Step 2] Working Correlation 추정...")
        alpha = self.compute_working_correlation(y, mu, cluster_ids, 'exchangeable')

        # 5. Sandwich variance (robust SE)
        logger.info("\n[Step 3] Robust Standard Errors 계산...")
        V_robust = self.sandwich_variance(X, y, mu, cluster_ids, alpha)
        robust_se = np.sqrt(np.diag(V_robust))

        # 6. Wald tests
        z_scores = beta / robust_se
        p_values = 2 * (1 - optimize.minimize(lambda x: abs(x), z_scores[0]).fun)  # Two-tailed
        # 간단한 z-test p-value 계산
        from scipy.stats import norm
        p_values = 2 * (1 - norm.cdf(np.abs(z_scores)))

        # 결과 저장
        self.coefficients = beta
        self.robust_se = robust_se
        self.covariance_matrix = V_robust

        # Variable names
        var_names = ['Intercept', 'Mode (Assisted vs Unaided)']
        if include_reader:
            var_names.append('Reader ID')

        # 결과 정리
        self.results = {
            'coefficients': {
                var_names[i]: {
                    'beta': float(beta[i]),
                    'se_robust': float(robust_se[i]),
                    'z': float(z_scores[i]),
                    'p_value': float(p_values[i]),
                    'ci_lower': float(beta[i] - 1.96 * robust_se[i]),
                    'ci_upper': float(beta[i] + 1.96 * robust_se[i]),
                    'OR': float(np.exp(beta[i])),  # Odds Ratio
                    'OR_ci_lower': float(np.exp(beta[i] - 1.96 * robust_se[i])),
                    'OR_ci_upper': float(np.exp(beta[i] + 1.96 * robust_se[i]))
                }
                for i in range(len(beta))
            },
            'correlation': {
                'structure': 'exchangeable',
                'alpha': float(alpha)
            },
            'model_info': {
                'n_obs': len(y),
                'n_clusters': len(set(cluster_ids)),
                'mean_cluster_size': float(np.mean(cluster_sizes)),
                'n_covariates': X.shape[1]
            }
        }

        # 결과 출력
        logger.info("\n" + "=" * 80)
        logger.info("GEE 결과")
        logger.info("=" * 80)
        logger.info(f"\nModel: Binomial family, Logit link, Exchangeable correlation")
        logger.info(f"N observations: {len(y)}, N clusters: {len(set(cluster_ids))}")
        logger.info(f"Working correlation: α={alpha:.3f}\n")

        logger.info("Coefficients:")
        logger.info("-" * 80)
        logger.info(f"{'Variable':<30} {'Beta':>10} {'SE':>10} {'z':>10} {'P>|z|':>10} {'OR':>10}")
        logger.info("-" * 80)

        for var_name, coef_data in self.results['coefficients'].items():
            sig = "***" if coef_data['p_value'] < 0.001 else "**" if coef_data['p_value'] < 0.01 else "*" if coef_data['p_value'] < 0.05 else ""
            logger.info(f"{var_name:<30} {coef_data['beta']:>10.4f} {coef_data['se_robust']:>10.4f} "
                       f"{coef_data['z']:>10.3f} {coef_data['p_value']:>10.4f} {coef_data['OR']:>10.3f} {sig}")

        logger.info("-" * 80)
        logger.info("\n95% Confidence Intervals:")
        for var_name, coef_data in self.results['coefficients'].items():
            logger.info(f"  {var_name}:")
            logger.info(f"    Beta: [{coef_data['ci_lower']:.4f}, {coef_data['ci_upper']:.4f}]")
            logger.info(f"    OR:   [{coef_data['OR_ci_lower']:.4f}, {coef_data['OR_ci_upper']:.4f}]")

        logger.info("\nGEE 분석 완료!")

        return self.results

    def export_results(self, output_dir: Path) -> Dict[str, Path]:
        """
        GEE 결과를 파일로 저장

        Args:
            output_dir: 출력 디렉토리

        Returns:
            저장된 파일 경로 딕셔너리
        """
        if not self.results:
            logger.warning("저장할 GEE 결과가 없습니다.")
            return {}

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 1. JSON 저장
        json_file = output_dir / "gee_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        saved_files['json'] = json_file
        logger.info(f"✓ JSON 저장: {json_file}")

        # 2. CSV 저장 (계수 테이블)
        csv_file = output_dir / "gee_coefficients.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Variable', 'Beta', 'SE_Robust', 'z', 'P_value', 'CI_Lower', 'CI_Upper',
                         'OR', 'OR_CI_Lower', 'OR_CI_Upper']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for var_name, coef_data in self.results['coefficients'].items():
                writer.writerow({
                    'Variable': var_name,
                    'Beta': f"{coef_data['beta']:.4f}",
                    'SE_Robust': f"{coef_data['se_robust']:.4f}",
                    'z': f"{coef_data['z']:.3f}",
                    'P_value': f"{coef_data['p_value']:.4f}",
                    'CI_Lower': f"{coef_data['ci_lower']:.4f}",
                    'CI_Upper': f"{coef_data['ci_upper']:.4f}",
                    'OR': f"{coef_data['OR']:.4f}",
                    'OR_CI_Lower': f"{coef_data['OR_ci_lower']:.4f}",
                    'OR_CI_Upper': f"{coef_data['OR_ci_upper']:.4f}"
                })

        saved_files['csv'] = csv_file
        logger.info(f"✓ CSV 저장: {csv_file}")

        # 3. Markdown 리포트
        md_file = output_dir / "gee_report.md"
        self._export_markdown_report(md_file)
        saved_files['markdown'] = md_file
        logger.info(f"✓ Markdown 저장: {md_file}")

        return saved_files

    def _export_markdown_report(self, filepath: Path):
        """Markdown 리포트 생성"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# GEE Analysis Report\n\n")

            # Model info
            model_info = self.results['model_info']
            f.write("## Model Specification\n\n")
            f.write(f"- **Family**: Binomial\n")
            f.write(f"- **Link**: Logit\n")
            f.write(f"- **Correlation Structure**: Exchangeable\n")
            f.write(f"- **Working Correlation**: α={self.results['correlation']['alpha']:.3f}\n\n")

            f.write("## Sample Information\n\n")
            f.write(f"- **N observations**: {model_info['n_obs']}\n")
            f.write(f"- **N clusters (patients)**: {model_info['n_clusters']}\n")
            f.write(f"- **Mean cluster size**: {model_info['mean_cluster_size']:.1f}\n")
            f.write(f"- **N covariates**: {model_info['n_covariates']}\n\n")

            # Coefficients table
            f.write("## Coefficients\n\n")
            f.write("| Variable | Beta | SE (Robust) | z | P>|z| | OR | 95% CI (OR) |\n")
            f.write("|----------|------|-------------|---|-------|----|--------------|\n")

            for var_name, coef_data in self.results['coefficients'].items():
                sig = "***" if coef_data['p_value'] < 0.001 else "**" if coef_data['p_value'] < 0.01 else "*" if coef_data['p_value'] < 0.05 else ""
                f.write(f"| {var_name} | {coef_data['beta']:.4f} | {coef_data['se_robust']:.4f} | "
                       f"{coef_data['z']:.3f} | {coef_data['p_value']:.4f}{sig} | {coef_data['OR']:.3f} | "
                       f"[{coef_data['OR_ci_lower']:.3f}, {coef_data['OR_ci_upper']:.3f}] |\n")

            f.write("\n**Significance codes**: *** p<0.001, ** p<0.01, * p<0.05\n\n")

            # Interpretation
            f.write("## Interpretation\n\n")
            mode_coef = self.results['coefficients']['Mode (Assisted vs Unaided)']
            f.write(f"**AI Assistance Effect**:\n\n")
            f.write(f"- **Odds Ratio**: {mode_coef['OR']:.3f}\n")
            f.write(f"- **95% CI**: [{mode_coef['OR_ci_lower']:.3f}, {mode_coef['OR_ci_upper']:.3f}]\n")
            f.write(f"- **P-value**: {mode_coef['p_value']:.4f}\n\n")

            if mode_coef['OR'] > 1:
                f.write(f"AI assistance **increases** the odds of positive detection by "
                       f"{(mode_coef['OR'] - 1) * 100:.1f}%.\n")
            else:
                f.write(f"AI assistance **decreases** the odds of positive detection by "
                       f"{(1 - mode_coef['OR']) * 100:.1f}%.\n")
