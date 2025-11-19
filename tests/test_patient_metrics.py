"""
FR-02: Patient-level Metrics 테스트

환자단위 지표 계산을 테스트합니다.
"""

import pandas as pd
import pytest

from src.patient_metrics import PatientMetricsCalculator


class TestPatientMetricsCalculator:
    """PatientMetricsCalculator 클래스 테스트"""

    @pytest.fixture
    def sample_data(self):
        """
        테스트용 샘플 데이터 생성

        3명의 환자, assisted/unaided 각각
        - P001: 실제 병변 있음 (GT=1), 예측 맞춤 (Pred=1)
        - P002: 실제 병변 없음 (GT=0), 예측 맞춤 (Pred=0)
        - P003: 실제 병변 있음 (GT=1), 예측 놓침 (Pred=0)
        """
        data = {
            "patient_id": ["P001", "P001", "P002", "P003"] * 2,
            "mode": ["assisted"] * 4 + ["unaided"] * 4,
            "ground_truth": [1, 0, 0, 1, 1, 0, 0, 1],  # P001에 병변 있음, P003에 병변 있음
            "prediction": [1, 0, 0, 0, 1, 0, 0, 0],  # assisted는 P001만 맞춤, unaided는 P001만 맞춤
        }

        return pd.DataFrame(data)

    @pytest.fixture
    def calculator(self):
        """테스트용 Calculator 인스턴스"""
        return PatientMetricsCalculator()

    def test_aggregate_patient_level(self, calculator, sample_data):
        """환자 단위 집계 테스트"""
        patient_df = calculator.aggregate_patient_level(sample_data)

        # 3명 환자 × 2 모드 = 6 rows
        assert len(patient_df) == 6

        # P001 (assisted): GT=1 (병변 있음), Pred=1 (예측 맞춤)
        p001_assisted = patient_df[
            (patient_df["patient_id"] == "P001")
            & (patient_df["mode"] == "assisted")
        ]
        assert p001_assisted["gt_patient"].values[0] == 1
        assert p001_assisted["pred_patient"].values[0] == 1

        # P002 (assisted): GT=0 (병변 없음), Pred=0 (예측 맞춤)
        p002_assisted = patient_df[
            (patient_df["patient_id"] == "P002")
            & (patient_df["mode"] == "assisted")
        ]
        assert p002_assisted["gt_patient"].values[0] == 0
        assert p002_assisted["pred_patient"].values[0] == 0

    def test_calculate_confusion_matrix(self, calculator):
        """Confusion matrix 계산 테스트"""
        gt = pd.Series([1, 1, 0, 0])
        pred = pd.Series([1, 0, 0, 1])

        cm = calculator.calculate_confusion_matrix(gt, pred)

        assert cm["TP"] == 1  # GT=1, Pred=1
        assert cm["FN"] == 1  # GT=1, Pred=0
        assert cm["TN"] == 1  # GT=0, Pred=0
        assert cm["FP"] == 1  # GT=0, Pred=1

    def test_calculate_metrics(self, calculator):
        """성능 지표 계산 테스트"""
        cm = {"TP": 80, "FP": 20, "FN": 10, "TN": 90}

        metrics = calculator.calculate_metrics(cm)

        # Sensitivity = TP / (TP + FN) = 80 / (80 + 10) = 0.889
        assert metrics["sensitivity"] == pytest.approx(80 / 90, abs=1e-3)

        # Specificity = TN / (TN + FP) = 90 / (90 + 20) = 0.818
        assert metrics["specificity"] == pytest.approx(90 / 110, abs=1e-3)

        # PPV = TP / (TP + FP) = 80 / (80 + 20) = 0.8
        assert metrics["ppv"] == pytest.approx(80 / 100, abs=1e-3)

        # NPV = TN / (TN + FN) = 90 / (90 + 10) = 0.9
        assert metrics["npv"] == pytest.approx(90 / 100, abs=1e-3)

    def test_calculate_metrics_edge_cases(self, calculator):
        """경계 케이스 테스트"""
        # 모든 TP인 경우
        cm_all_tp = {"TP": 100, "FP": 0, "FN": 0, "TN": 0}
        metrics = calculator.calculate_metrics(cm_all_tp)
        assert metrics["sensitivity"] == 1.0
        assert metrics["ppv"] == 1.0

        # 모든 TN인 경우
        cm_all_tn = {"TP": 0, "FP": 0, "FN": 0, "TN": 100}
        metrics = calculator.calculate_metrics(cm_all_tn)
        assert metrics["specificity"] == 1.0
        assert metrics["npv"] == 1.0

        # Division by zero 방지 확인
        cm_zero = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
        metrics = calculator.calculate_metrics(cm_zero)
        assert metrics["sensitivity"] == 0.0
        assert metrics["specificity"] == 0.0

    def test_calculate_by_mode(self, calculator, sample_data):
        """Mode별 지표 계산 테스트"""
        results = calculator.calculate_by_mode(sample_data)

        # Assisted와 Unaided 모두 계산되어야 함
        assert "assisted" in results
        assert "unaided" in results

        # 각 mode별로 confusion matrix와 metrics 존재
        for mode in ["assisted", "unaided"]:
            assert "confusion_matrix" in results[mode]
            assert "metrics" in results[mode]
            assert "n_patients" in results[mode]

            # 3명의 환자
            assert results[mode]["n_patients"] == 3

            # Metrics의 모든 키 존재
            metrics = results[mode]["metrics"]
            assert "sensitivity" in metrics
            assert "specificity" in metrics
            assert "ppv" in metrics
            assert "npv" in metrics

    def test_calculate_delta(self, calculator, sample_data):
        """Delta (Assisted - Unaided) 계산 테스트"""
        # 먼저 mode별 계산 수행
        calculator.calculate_by_mode(sample_data)

        # Delta 계산
        delta = calculator.calculate_delta()

        # Delta 키 확인
        assert "delta_sensitivity" in delta
        assert "delta_specificity" in delta
        assert "delta_ppv" in delta
        assert "delta_npv" in delta

        # Delta 값은 -1 ~ 1 사이
        for key, value in delta.items():
            assert -1 <= value <= 1

    def test_calculate_delta_before_metrics(self, calculator):
        """Metrics 계산 전 Delta 계산 시도 시 에러"""
        with pytest.raises(ValueError, match="계산되어야 합니다"):
            calculator.calculate_delta()

    def test_create_comparison_table(self, calculator, sample_data):
        """비교 테이블 생성 테스트"""
        calculator.calculate_by_mode(sample_data)

        table = calculator.create_comparison_table()

        # 4개 metrics (Sensitivity, Specificity, PPV, NPV)
        assert len(table) == 4

        # 컬럼 확인
        assert "Metric" in table.columns
        assert "Assisted" in table.columns
        assert "Unaided" in table.columns
        assert "Δ (Assisted - Unaided)" in table.columns

        # Metric 이름 확인
        metrics_in_table = set(table["Metric"].str.lower())
        assert "sensitivity" in metrics_in_table
        assert "specificity" in metrics_in_table
        assert "ppv" in metrics_in_table
        assert "npv" in metrics_in_table

    def test_create_confusion_matrix_table(self, calculator, sample_data):
        """Confusion matrix 테이블 생성 테스트"""
        calculator.calculate_by_mode(sample_data)

        cm_table = calculator.create_confusion_matrix_table(mode="assisted")

        # 2x2 테이블
        assert cm_table.shape == (2, 2)

        # 인덱스와 컬럼 확인
        assert "Actual Positive" in cm_table.index
        assert "Actual Negative" in cm_table.index
        assert "Predicted Positive" in cm_table.columns
        assert "Predicted Negative" in cm_table.columns

    def test_perfect_classifier(self, calculator):
        """완벽한 분류기 테스트"""
        # 모든 예측이 정확한 경우
        perfect_data = pd.DataFrame(
            {
                "patient_id": ["P001", "P002", "P003", "P004"],
                "mode": ["assisted"] * 4,
                "ground_truth": [1, 1, 0, 0],
                "prediction": [1, 1, 0, 0],
            }
        )

        results = calculator.calculate_by_mode(perfect_data)

        metrics = results["assisted"]["metrics"]

        # 모든 지표가 1.0이어야 함
        assert metrics["sensitivity"] == 1.0
        assert metrics["specificity"] == 1.0
        assert metrics["ppv"] == 1.0
        assert metrics["npv"] == 1.0

    def test_worst_classifier(self, calculator):
        """최악의 분류기 테스트"""
        # 모든 예측이 틀린 경우
        worst_data = pd.DataFrame(
            {
                "patient_id": ["P001", "P002", "P003", "P004"],
                "mode": ["assisted"] * 4,
                "ground_truth": [1, 1, 0, 0],
                "prediction": [0, 0, 1, 1],
            }
        )

        results = calculator.calculate_by_mode(worst_data)

        metrics = results["assisted"]["metrics"]

        # 모든 지표가 0.0이어야 함
        assert metrics["sensitivity"] == 0.0
        assert metrics["specificity"] == 0.0
        assert metrics["ppv"] == 0.0
        assert metrics["npv"] == 0.0


# 통합 테스트
class TestPatientMetricsIntegration:
    """통합 테스트"""

    def test_full_pipeline(self):
        """전체 파이프라인 테스트"""
        # 실제적인 데이터 생성
        data = {
            "patient_id": [f"P{i:03d}" for i in range(1, 101)] * 2,  # 100명 환자
            "mode": ["assisted"] * 100 + ["unaided"] * 100,
            "ground_truth": [1] * 60 + [0] * 40 + [1] * 60 + [0] * 40,  # 60% 유병률
            "prediction": (
                [1] * 55 + [0] * 5 + [1] * 5 + [0] * 35  # Assisted: Se=91.7%, Sp=87.5%
                + [1] * 50 + [0] * 10 + [1] * 8 + [0] * 32  # Unaided: Se=83.3%, Sp=80%
            ),
        }

        df = pd.DataFrame(data)

        calculator = PatientMetricsCalculator()
        results = calculator.calculate_by_mode(df)

        # Assisted가 Unaided보다 성능이 좋아야 함
        assert (
            results["assisted"]["metrics"]["sensitivity"]
            >= results["unaided"]["metrics"]["sensitivity"]
        )
        assert (
            results["assisted"]["metrics"]["specificity"]
            >= results["unaided"]["metrics"]["specificity"]
        )

        # Delta 확인
        delta = calculator.calculate_delta()
        assert delta["delta_sensitivity"] >= 0
        assert delta["delta_specificity"] >= 0

        # 비교 테이블 생성
        table = calculator.create_comparison_table()
        assert len(table) == 4
