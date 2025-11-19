"""
FR-01: 데이터 로더 테스트

데이터 로딩, 스키마 검증, 품질 체크 기능을 테스트합니다.
"""

import pandas as pd
import pytest

from src.data_loader import DataLoader


class TestDataLoader:
    """DataLoader 클래스 테스트"""

    @pytest.fixture
    def sample_data(self):
        """
        테스트용 샘플 데이터 생성
        """
        return pd.DataFrame(
            {
                "patient_id": ["P001", "P001", "P002", "P003"],
                "image_id": ["I001", "I002", "I003", "I004"],
                "mode": ["assisted", "unaided", "assisted", "unaided"],
                "prediction": [1, 0, 1, 0],
                "ground_truth": [1, 0, 0, 0],
            }
        )

    @pytest.fixture
    def loader(self):
        """
        테스트용 DataLoader 인스턴스
        """
        return DataLoader()

    def test_validate_schema_success(self, loader, sample_data):
        """
        정상 스키마 검증 테스트
        """
        result = loader.validate_schema(sample_data, "TEST")
        assert result is True

    def test_validate_schema_empty(self, loader):
        """
        빈 데이터프레임 검증 테스트
        """
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="비어있습니다"):
            loader.validate_schema(empty_df, "TEST")

    def test_check_missing_values_none(self, loader, sample_data):
        """
        결측치 없는 경우 테스트
        """
        report = loader.check_missing_values(sample_data, "TEST")
        assert report["total_rows"] == 4
        assert len(report["missing_by_column"]) == 0

    def test_check_missing_values_exists(self, loader):
        """
        결측치 있는 경우 테스트
        """
        df_with_missing = pd.DataFrame(
            {
                "patient_id": ["P001", "P002", None],
                "prediction": [1, None, 0],
            }
        )

        report = loader.check_missing_values(df_with_missing, "TEST")
        assert report["total_rows"] == 3
        assert "patient_id" in report["missing_by_column"]
        assert report["missing_by_column"]["patient_id"] == 1
        assert "prediction" in report["missing_by_column"]
        assert report["missing_by_column"]["prediction"] == 1

    def test_check_duplicates_none(self, loader, sample_data):
        """
        중복 없는 경우 테스트
        """
        report = loader.check_duplicates(sample_data, "TEST")
        assert report["n_duplicates"] == 0
        assert report["duplicate_percentage"] == 0

    def test_check_duplicates_exists(self, loader):
        """
        중복 있는 경우 테스트
        """
        df_with_dup = pd.DataFrame(
            {
                "patient_id": ["P001", "P001", "P002"],
                "value": [1, 1, 2],
            }
        )

        report = loader.check_duplicates(df_with_dup, "TEST")
        assert report["n_duplicates"] == 1

    def test_generate_quality_report(self, loader, sample_data):
        """
        품질 리포트 생성 테스트
        """
        report = loader.generate_quality_report(sample_data, "BCR")

        assert report["reader_type"] == "BCR"
        assert "Board-certified Radiologist" in report["reader_description"]
        assert report["total_rows"] == 4
        assert report["total_columns"] == 5
        assert "patient_id" in report["columns"]
        assert "missing_values" in report
        assert "duplicates" in report

    def test_get_combined_data_not_loaded(self, loader):
        """
        데이터 로딩 전 결합 시도 테스트
        """
        with pytest.raises(ValueError, match="로딩되지 않았습니다"):
            loader.get_combined_data()


# 실제 파일 로딩 테스트 (실제 파일 존재 시)
class TestDataLoaderWithRealFiles:
    """실제 Excel 파일 로딩 테스트"""

    @pytest.fixture
    def loader(self):
        return DataLoader()

    @pytest.mark.skipif(
        True, reason="실제 파일 구조 확인 후 활성화"
    )
    def test_load_all_real_files(self, loader):
        """
        실제 파일 로딩 테스트 (스킵됨 - 파일 구조 확인 필요)
        """
        data = loader.load_all()

        assert "BCR" in data
        assert "EMS" in data
        assert "RESIDENT" in data

        for reader_type, df in data.items():
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
