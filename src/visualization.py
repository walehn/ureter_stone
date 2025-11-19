"""
FR-07: Visualization Module

모든 분석 결과를 논문 제출 가능한 그래프로 시각화합니다.

주요 기능:
- Bootstrap 분포 히스토그램
- Decision Curve Analysis 그래프
- Patient-level/Lesion-level 성능 비교 막대 그래프
- Confusion Matrix 히트맵
- 300 dpi PNG 출력
- Color-blind friendly 색상
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from .logger import setup_logger

logger = setup_logger(__name__)


class Visualizer:
    """
    분석 결과 시각화 클래스

    모든 그래프는 300 dpi, publication-ready 형식으로 출력됩니다.
    """

    # Color-blind friendly palette (Wong 2011)
    COLORS = {
        'blue': '#0173B2',      # Assisted
        'orange': '#DE8F05',    # Unaided
        'green': '#029E73',     # Positive
        'red': '#CC78BC',       # Negative
        'gray': '#949494',      # Neutral
        'yellow': '#ECE133',    # Highlight
        'skyblue': '#56B4E9',   # Light blue
        'vermillion': '#D55E00' # Red-orange
    }

    def __init__(self, dpi: int = 300, figsize: Tuple[int, int] = (10, 6)):
        """
        초기화

        Args:
            dpi: 출력 해상도 (기본 300)
            figsize: 기본 그래프 크기
        """
        self.dpi = dpi
        self.figsize = figsize

        # Matplotlib 스타일 설정
        plt.rcParams['figure.dpi'] = dpi
        plt.rcParams['savefig.dpi'] = dpi
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['figure.facecolor'] = 'white'

        logger.info(f"Visualizer 초기화: dpi={dpi}, figsize={figsize}")

    def plot_bootstrap_distribution(self,
                                    bootstrap_samples: np.ndarray,
                                    metric_name: str,
                                    ci_lower: float,
                                    ci_upper: float,
                                    observed_value: float,
                                    output_path: Path,
                                    title: str = "Bootstrap Distribution") -> Path:
        """
        Bootstrap 분포 히스토그램

        Args:
            bootstrap_samples: Bootstrap 샘플 배열
            metric_name: 지표 이름 (e.g., "Sensitivity")
            ci_lower: 95% CI 하한
            ci_upper: 95% CI 상한
            observed_value: 관찰값
            output_path: 저장 경로
            title: 그래프 제목

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # 히스토그램
        ax.hist(bootstrap_samples, bins=50, color=self.COLORS['blue'],
                alpha=0.7, edgecolor='black', linewidth=0.5)

        # 95% CI 수직선
        ax.axvline(ci_lower, color=self.COLORS['red'], linestyle='--',
                   linewidth=2, label=f'95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]')
        ax.axvline(ci_upper, color=self.COLORS['red'], linestyle='--', linewidth=2)

        # 관찰값
        ax.axvline(observed_value, color=self.COLORS['green'], linestyle='-',
                   linewidth=2, label=f'Observed: {observed_value:.4f}')

        ax.set_xlabel(metric_name, fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Bootstrap 분포 저장: {output_path}")
        return output_path

    def plot_decision_curve(self,
                           thresholds: np.ndarray,
                           nb_assisted: np.ndarray,
                           nb_unaided: np.ndarray,
                           nb_treat_all: np.ndarray,
                           nb_treat_none: np.ndarray,
                           output_path: Path,
                           title: str = "Decision Curve Analysis") -> Path:
        """
        Decision Curve Analysis 그래프

        Args:
            thresholds: Threshold 배열
            nb_assisted: Assisted Net Benefit
            nb_unaided: Unaided Net Benefit
            nb_treat_all: Treat All Net Benefit
            nb_treat_none: Treat None Net Benefit
            output_path: 저장 경로
            title: 그래프 제목

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Net Benefit 곡선
        ax.plot(thresholds, nb_assisted, color=self.COLORS['blue'],
                linewidth=2.5, label='Assisted (With AI)', marker='o',
                markersize=4, markevery=5)
        ax.plot(thresholds, nb_unaided, color=self.COLORS['orange'],
                linewidth=2.5, label='Unaided (Without AI)', marker='s',
                markersize=4, markevery=5)
        ax.plot(thresholds, nb_treat_all, color=self.COLORS['gray'],
                linewidth=1.5, linestyle='--', label='Treat All', alpha=0.7)
        ax.plot(thresholds, nb_treat_none, color=self.COLORS['gray'],
                linewidth=1.5, linestyle=':', label='Treat None', alpha=0.7)

        ax.set_xlabel('Threshold Probability', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net Benefit', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([thresholds.min(), thresholds.max()])

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Decision Curve 저장: {output_path}")
        return output_path

    def plot_metrics_comparison(self,
                               metrics_assisted: Dict[str, float],
                               metrics_unaided: Dict[str, float],
                               metric_names: List[str],
                               output_path: Path,
                               title: str = "Performance Metrics Comparison",
                               ylabel: str = "Value") -> Path:
        """
        성능 지표 비교 막대 그래프

        Args:
            metrics_assisted: Assisted 지표 딕셔너리
            metrics_unaided: Unaided 지표 딕셔너리
            metric_names: 표시할 지표 이름 리스트
            output_path: 저장 경로
            title: 그래프 제목
            ylabel: Y축 라벨

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        x = np.arange(len(metric_names))
        width = 0.35

        assisted_values = [metrics_assisted.get(m, 0) for m in metric_names]
        unaided_values = [metrics_unaided.get(m, 0) for m in metric_names]

        # 막대 그래프
        bars1 = ax.bar(x - width/2, assisted_values, width,
                       label='Assisted (With AI)',
                       color=self.COLORS['blue'], edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x + width/2, unaided_values, width,
                       label='Unaided (Without AI)',
                       color=self.COLORS['orange'], edgecolor='black', linewidth=0.5)

        # 값 라벨 추가
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names, rotation=0)
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1.1])

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Metrics 비교 그래프 저장: {output_path}")
        return output_path

    def plot_confusion_matrix(self,
                             tp: int, fp: int, fn: int, tn: int,
                             output_path: Path,
                             title: str = "Confusion Matrix") -> Path:
        """
        Confusion Matrix 히트맵

        Args:
            tp, fp, fn, tn: Confusion matrix 값
            output_path: 저장 경로
            title: 그래프 제목

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Confusion matrix 배열
        cm = np.array([[tn, fp], [fn, tp]])

        # 히트맵 (색상만, 숫자는 별도 추가)
        im = ax.imshow(cm, cmap='Blues', alpha=0.8)

        # 축 설정
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Predicted\nNegative', 'Predicted\nPositive'], fontsize=11)
        ax.set_yticklabels(['Actual\nNegative', 'Actual\nPositive'], fontsize=11)

        ax.set_xlabel('Predicted', fontsize=12, fontweight='bold')
        ax.set_ylabel('Actual', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # 텍스트 추가
        labels = [['TN', 'FP'], ['FN', 'TP']]
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, f'{labels[i][j]}\n{cm[i, j]}',
                              ha="center", va="center",
                              color="white" if cm[i, j] > cm.max()/2 else "black",
                              fontsize=16, fontweight='bold')

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Count', rotation=270, labelpad=20, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Confusion Matrix 저장: {output_path}")
        return output_path

    def plot_delta_comparison(self,
                             reader_names: List[str],
                             deltas: Dict[str, Dict[str, float]],
                             metric_name: str,
                             output_path: Path,
                             title: str = "Delta Comparison Across Readers") -> Path:
        """
        리더별 Delta 비교 막대 그래프

        Args:
            reader_names: 리더 이름 리스트
            deltas: {reader_name: {metric: delta_value}}
            metric_name: 비교할 지표 이름
            output_path: 저장 경로
            title: 그래프 제목

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        x = np.arange(len(reader_names))
        delta_values = [deltas[reader].get(metric_name, 0) for reader in reader_names]

        # 색상: 양수=파랑, 음수=빨강
        colors = [self.COLORS['blue'] if v >= 0 else self.COLORS['red']
                  for v in delta_values]

        bars = ax.bar(x, delta_values, color=colors, edgecolor='black', linewidth=1)

        # 값 라벨
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:+.4f}\n({height*100:+.2f}%)',
                   ha='center', va='bottom' if height >= 0 else 'top',
                   fontsize=10, fontweight='bold')

        # 0 기준선
        ax.axhline(0, color='black', linewidth=1, linestyle='-')

        ax.set_xlabel('Reader', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Δ {metric_name} (Assisted - Unaided)',
                     fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(reader_names)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Delta 비교 그래프 저장: {output_path}")
        return output_path

    def plot_precision_recall_curve(self,
                                    precision_assisted: float,
                                    recall_assisted: float,
                                    precision_unaided: float,
                                    recall_unaided: float,
                                    output_path: Path,
                                    title: str = "Precision-Recall Comparison") -> Path:
        """
        Precision-Recall 포인트 비교 그래프

        Args:
            precision_assisted, recall_assisted: Assisted 지표
            precision_unaided, recall_unaided: Unaided 지표
            output_path: 저장 경로
            title: 그래프 제목

        Returns:
            저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        # Assisted 포인트
        ax.scatter(recall_assisted, precision_assisted,
                  s=300, color=self.COLORS['blue'],
                  marker='o', edgecolor='black', linewidth=2,
                  label='Assisted (With AI)', zorder=3)

        # Unaided 포인트
        ax.scatter(recall_unaided, precision_unaided,
                  s=300, color=self.COLORS['orange'],
                  marker='s', edgecolor='black', linewidth=2,
                  label='Unaided (Without AI)', zorder=3)

        # 화살표 (Unaided → Assisted)
        ax.annotate('', xy=(recall_assisted, precision_assisted),
                   xytext=(recall_unaided, precision_unaided),
                   arrowprops=dict(arrowstyle='->', lw=2, color='gray', alpha=0.6))

        # 값 라벨
        ax.text(recall_assisted, precision_assisted,
               f'  ({recall_assisted:.3f}, {precision_assisted:.3f})',
               ha='left', va='bottom', fontsize=10, fontweight='bold')
        ax.text(recall_unaided, precision_unaided,
               f'  ({recall_unaided:.3f}, {precision_unaided:.3f})',
               ha='left', va='top', fontsize=10, fontweight='bold')

        ax.set_xlabel('Recall (Sensitivity)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Precision (PPV)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', frameon=True, shadow=True, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])

        # 대각선 (iso-F1 참고선)
        x_diag = np.linspace(0, 1, 100)
        for f1 in [0.2, 0.4, 0.6, 0.8]:
            y_diag = (f1 * x_diag) / (2 * x_diag - f1)
            y_diag = np.where((y_diag >= 0) & (y_diag <= 1), y_diag, np.nan)
            ax.plot(x_diag, y_diag, 'k--', alpha=0.2, linewidth=0.5)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"✓ Precision-Recall 그래프 저장: {output_path}")
        return output_path
