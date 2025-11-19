"""
FR-02: 환자단위 지표 계산 모듈

환자 단위로 Sensitivity, Specificity, PPV, NPV를 계산합니다.
"""

from typing import Dict, List, Tuple

import pandas as pd

from src.constants import MODE_ASSISTED, MODE_UNAIDED, PATIENT_METRICS
from src.logger import get_logger

logger = get_logger()


class PatientMetricsCalculator:
    """
    환자단위 성능 지표 계산기

    개별 병변이 아닌 환자 전체를 단위로 성능을 평가합니다.
    환자에게 병변이 하나라도 있으면 Positive로 간주합니다.
    """

    def __init__(self):
        """초기화"""
        self.metrics = {}
        self.confusion_matrices = {}

    def aggregate_patient_level(
        self, df: pd.DataFrame, patient_col: str = "patient_id"
    ) -> pd.DataFrame:
        """
        환자 단위로 데이터를 집계합니다.

        각 환자에 대해:
        - Ground truth: 실제 병변이 1개 이상 있으면 1, 없으면 0
        - Prediction: 예측한 병변이 1개 이상 있으면 1, 없으면 0

        Args:
            df: 원본 데이터프레임 (patient_id, mode, ground_truth, prediction 컬럼 필요)
            patient_col: 환자 ID 컬럼명

        Returns:
            환자 단위로 집계된 DataFrame (patient_id, mode, gt_patient, pred_patient)
        """
        # 환자별로 그룹화
        patient_agg = (
            df.groupby([patient_col, "mode"])
            .agg(
                {
                    "ground_truth": lambda x: 1
                    if x.sum() > 0
                    else 0,  # 하나라도 있으면 1
                    "prediction": lambda x: 1 if x.sum() > 0 else 0,
                }
            )
            .reset_index()
        )

        patient_agg.columns = [patient_col, "mode", "gt_patient", "pred_patient"]

        logger.debug(
            f"환자 단위 집계 완료: {len(patient_agg)} 환자-모드 조합"
        )

        return patient_agg

    def calculate_confusion_matrix(
        self, gt: pd.Series, pred: pd.Series
    ) -> Dict[str, int]:
        """
        Confusion matrix를 계산합니다.

        Args:
            gt: Ground truth (0 or 1)
            pred: Prediction (0 or 1)

        Returns:
            TP, FP, FN, TN을 포함하는 딕셔너리
        """
        tp = ((gt == 1) & (pred == 1)).sum()
        fp = ((gt == 0) & (pred == 1)).sum()
        fn = ((gt == 1) & (pred == 0)).sum()
        tn = ((gt == 0) & (pred == 0)).sum()

        return {
            "TP": int(tp),
            "FP": int(fp),
            "FN": int(fn),
            "TN": int(tn),
        }

    def calculate_metrics(self, cm: Dict[str, int]) -> Dict[str, float]:
        """
        Confusion matrix로부터 성능 지표를 계산합니다.

        Args:
            cm: Confusion matrix (TP, FP, FN, TN)

        Returns:
            Sensitivity, Specificity, PPV, NPV를 포함하는 딕셔너리
        """
        tp = cm["TP"]
        fp = cm["FP"]
        fn = cm["FN"]
        tn = cm["TN"]

        # Sensitivity (Recall): TP / (TP + FN)
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # Specificity: TN / (TN + FP)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        # PPV (Precision): TP / (TP + FP)
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # NPV: TN / (TN + FN)
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0

        return {
            "sensitivity": sensitivity,
            "specificity": specificity,
            "ppv": ppv,
            "npv": npv,
        }

    def calculate_by_mode(
        self,
        df: pd.DataFrame,
        patient_col: str = "patient_id",
        mode_col: str = "mode",
    ) -> Dict[str, Dict]:
        """
        Mode (assisted vs unaided)별로 지표를 계산합니다.

        Args:
            df: 원본 데이터프레임
            patient_col: 환자 ID 컬럼명
            mode_col: Mode 컬럼명 (assisted/unaided)

        Returns:
            Mode별 confusion matrix 및 metrics를 포함하는 딕셔너리
        """
        # 환자 단위 집계
        patient_df = self.aggregate_patient_level(df, patient_col)

        results = {}

        for mode in [MODE_ASSISTED, MODE_UNAIDED]:
            mode_df = patient_df[patient_df[mode_col] == mode]

            if len(mode_df) == 0:
                logger.warning(f"{mode} 모드 데이터가 없습니다")
                continue

            # Confusion matrix 계산
            cm = self.calculate_confusion_matrix(
                mode_df["gt_patient"], mode_df["pred_patient"]
            )

            # 지표 계산
            metrics = self.calculate_metrics(cm)

            results[mode] = {
                "confusion_matrix": cm,
                "metrics": metrics,
                "n_patients": len(mode_df),
            }

            logger.info(
                f"{mode} 모드: Se={metrics['sensitivity']:.3f}, "
                f"Sp={metrics['specificity']:.3f}, "
                f"PPV={metrics['ppv']:.3f}, NPV={metrics['npv']:.3f}"
            )

        # 결과 저장
        self.confusion_matrices = {
            mode: res["confusion_matrix"] for mode, res in results.items()
        }
        self.metrics = {
            mode: res["metrics"] for mode, res in results.items()
        }

        return results

    def calculate_delta(self) -> Dict[str, float]:
        """
        Assisted와 Unaided 간 차이(Δ)를 계산합니다.

        Δ = Metric_assisted - Metric_unaided

        Returns:
            각 지표별 차이값을 포함하는 딕셔너리
        """
        if MODE_ASSISTED not in self.metrics or MODE_UNAIDED not in self.metrics:
            raise ValueError(
                "Assisted 및 Unaided 지표가 모두 계산되어야 합니다"
            )

        assisted = self.metrics[MODE_ASSISTED]
        unaided = self.metrics[MODE_UNAIDED]

        delta = {}

        for metric in PATIENT_METRICS:
            delta[f"delta_{metric}"] = assisted[metric] - unaided[metric]

        logger.info(
            f"Δ Sensitivity: {delta['delta_sensitivity']:.3f}, "
            f"Δ Specificity: {delta['delta_specificity']:.3f}"
        )

        return delta

    def create_comparison_table(self) -> pd.DataFrame:
        """
        Assisted vs Unaided 비교 테이블을 생성합니다.

        Returns:
            비교 테이블 DataFrame
        """
        if not self.metrics:
            raise ValueError("지표가 계산되지 않았습니다. calculate_by_mode()를 먼저 호출하세요")

        # 데이터 준비
        data = []

        for metric in PATIENT_METRICS:
            row = {
                "Metric": metric.upper(),
                "Assisted": self.metrics.get(MODE_ASSISTED, {}).get(
                    metric, 0.0
                ),
                "Unaided": self.metrics.get(MODE_UNAIDED, {}).get(metric, 0.0),
            }

            # Delta 계산
            if MODE_ASSISTED in self.metrics and MODE_UNAIDED in self.metrics:
                row["Δ (Assisted - Unaided)"] = (
                    row["Assisted"] - row["Unaided"]
                )

            data.append(row)

        df = pd.DataFrame(data)

        logger.info("비교 테이블 생성 완료")

        return df

    def create_confusion_matrix_table(
        self, mode: str = MODE_ASSISTED
    ) -> pd.DataFrame:
        """
        특정 mode의 confusion matrix를 DataFrame으로 생성합니다.

        Args:
            mode: Mode (assisted or unaided)

        Returns:
            Confusion matrix DataFrame
        """
        if mode not in self.confusion_matrices:
            raise ValueError(f"{mode} 모드의 confusion matrix가 없습니다")

        cm = self.confusion_matrices[mode]

        df = pd.DataFrame(
            {
                "Predicted Positive": [cm["TP"], cm["FN"]],
                "Predicted Negative": [cm["FP"], cm["TN"]],
            },
            index=["Actual Positive", "Actual Negative"],
        )

        return df

    def export_metrics(self, output_path: str) -> None:
        """
        계산된 지표를 JSON 파일로 저장합니다.

        Args:
            output_path: 출력 파일 경로
        """
        import json
        from pathlib import Path

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "confusion_matrices": self.confusion_matrices,
            "metrics": self.metrics,
        }

        # Delta 추가
        if MODE_ASSISTED in self.metrics and MODE_UNAIDED in self.metrics:
            export_data["delta"] = self.calculate_delta()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"지표 저장 완료: {output_file}")


def calculate_patient_metrics_from_data(
    df: pd.DataFrame, patient_col: str = "patient_id"
) -> PatientMetricsCalculator:
    """
    데이터로부터 환자단위 지표를 계산합니다.

    Args:
        df: 원본 데이터프레임
        patient_col: 환자 ID 컬럼명

    Returns:
        계산 완료된 PatientMetricsCalculator 객체
    """
    calculator = PatientMetricsCalculator()
    calculator.calculate_by_mode(df, patient_col=patient_col)

    return calculator
