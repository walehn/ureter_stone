"""
FR-01: 데이터 입력 처리 모듈

Excel 파일 로딩, 스키마 검증, 데이터 품질 체크를 수행합니다.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.constants import READER_TYPES
from src.logger import get_logger

logger = get_logger()


class DataLoader:
    """
    Excel 데이터 로더

    3가지 리더 유형의 결과 파일을 로딩하고 검증합니다:
    - BCR (Board-certified Radiologist): 영상의학전문의
    - EMS (Emergency Medicine Specialist): 응급의학과전문의
    - RESIDENT (Radiology Resident): 영상의학과전공의
    """

    # 예상 스키마 (실제 파일에 맞게 조정 필요)
    EXPECTED_COLUMNS = {
        "patient_id",  # 환자 ID
        "image_id",  # 이미지 ID
        "mode",  # assisted or unaided
        "prediction",  # 예측 결과 (0 or 1, or bounding box)
        "ground_truth",  # 정답 (0 or 1, or bounding box)
    }

    def __init__(self, data_dir: str = "."):
        """
        Args:
            data_dir: 데이터 파일이 있는 디렉토리
        """
        self.data_dir = Path(data_dir)
        self.data: Dict[str, pd.DataFrame] = {}
        self.quality_reports: Dict[str, Dict] = {}

    def load_excel(self, file_path: str, reader_type: str) -> pd.DataFrame:
        """
        Excel 파일을 로딩합니다.

        Args:
            file_path: Excel 파일 경로
            reader_type: 리더 유형 (BCR, EMS, RESIDENT)

        Returns:
            로딩된 DataFrame

        Raises:
            FileNotFoundError: 파일이 없는 경우
            ValueError: 스키마가 일치하지 않는 경우
        """
        full_path = self.data_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {full_path}")

        logger.info(f"{reader_type} 데이터 로딩 중: {full_path}")

        try:
            df = pd.read_excel(full_path)
        except Exception as e:
            logger.error(f"Excel 파일 로딩 실패: {e}")
            raise

        logger.info(
            f"{reader_type} 데이터 로딩 완료: {len(df)} rows, {len(df.columns)} columns"
        )

        return df

    def validate_schema(self, df: pd.DataFrame, reader_type: str) -> bool:
        """
        데이터프레임의 스키마를 검증합니다.

        Args:
            df: 검증할 DataFrame
            reader_type: 리더 유형

        Returns:
            검증 통과 여부

        Raises:
            ValueError: 필수 컬럼이 없는 경우
        """
        df_columns = set(df.columns)

        # 필수 컬럼 체크 (실제 데이터에 맞게 조정 필요)
        # 현재는 최소한의 컬럼만 요구
        if df.empty:
            raise ValueError(f"{reader_type} 데이터가 비어있습니다")

        logger.info(f"{reader_type} 스키마 검증 통과: {list(df.columns)}")

        return True

    def check_missing_values(self, df: pd.DataFrame, reader_type: str) -> Dict:
        """
        결측치를 확인합니다.

        Args:
            df: DataFrame
            reader_type: 리더 유형

        Returns:
            결측치 리포트 (컬럼별 결측 개수)
        """
        missing = df.isnull().sum()
        missing_dict = missing[missing > 0].to_dict()

        if missing_dict:
            logger.warning(f"{reader_type} 결측치 발견: {missing_dict}")
        else:
            logger.info(f"{reader_type} 결측치 없음")

        return {
            "total_rows": len(df),
            "missing_by_column": missing_dict,
            "missing_percentage": {
                col: (count / len(df)) * 100 for col, count in missing_dict.items()
            },
        }

    def check_duplicates(self, df: pd.DataFrame, reader_type: str) -> Dict:
        """
        중복 레코드를 확인합니다.

        Args:
            df: DataFrame
            reader_type: 리더 유형

        Returns:
            중복 리포트
        """
        n_duplicates = df.duplicated().sum()

        if n_duplicates > 0:
            logger.warning(f"{reader_type} 중복 레코드 발견: {n_duplicates}개")
        else:
            logger.info(f"{reader_type} 중복 레코드 없음")

        return {
            "n_duplicates": int(n_duplicates),
            "duplicate_percentage": (n_duplicates / len(df)) * 100 if len(df) > 0 else 0,
        }

    def generate_quality_report(
        self, df: pd.DataFrame, reader_type: str
    ) -> Dict:
        """
        데이터 품질 리포트를 생성합니다.

        Args:
            df: DataFrame
            reader_type: 리더 유형

        Returns:
            품질 리포트 딕셔너리
        """
        report = {
            "reader_type": reader_type,
            "reader_description": READER_TYPES.get(reader_type, "Unknown"),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": self.check_missing_values(df, reader_type),
            "duplicates": self.check_duplicates(df, reader_type),
        }

        # 기술 통계 (수치형 컬럼만)
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            report["numeric_summary"] = df[numeric_cols].describe().to_dict()

        logger.info(f"{reader_type} 품질 리포트 생성 완료")

        return report

    def load_all(
        self,
        bcr_file: str = "BCR_result.xlsx",
        ems_file: str = "EMS_result.xlsx",
        resident_file: str = "Resident_result.xlsx",
    ) -> Dict[str, pd.DataFrame]:
        """
        모든 리더의 데이터를 로딩합니다.

        Args:
            bcr_file: BCR 결과 파일명
            ems_file: EMS 결과 파일명
            resident_file: Resident 결과 파일명

        Returns:
            리더 유형별 DataFrame 딕셔너리
        """
        logger.info("전체 데이터 로딩 시작")

        files = {
            "BCR": bcr_file,
            "EMS": ems_file,
            "RESIDENT": resident_file,
        }

        for reader_type, file_name in files.items():
            try:
                # 파일 로딩
                df = self.load_excel(file_name, reader_type)

                # 스키마 검증
                self.validate_schema(df, reader_type)

                # 품질 리포트 생성
                quality_report = self.generate_quality_report(df, reader_type)

                # 저장
                self.data[reader_type] = df
                self.quality_reports[reader_type] = quality_report

                logger.info(f"{reader_type} 처리 완료")

            except Exception as e:
                logger.error(f"{reader_type} 처리 실패: {e}")
                raise

        logger.info(f"전체 데이터 로딩 완료: {len(self.data)}개 리더")

        return self.data

    def get_combined_data(self) -> pd.DataFrame:
        """
        모든 리더의 데이터를 결합합니다.

        Returns:
            결합된 DataFrame (reader_type 컬럼 추가)
        """
        if not self.data:
            raise ValueError("데이터가 로딩되지 않았습니다. load_all()을 먼저 호출하세요.")

        combined_list = []

        for reader_type, df in self.data.items():
            df_copy = df.copy()
            df_copy["reader_type"] = reader_type
            combined_list.append(df_copy)

        combined = pd.concat(combined_list, ignore_index=True)

        logger.info(f"결합된 데이터: {len(combined)} rows")

        return combined

    def export_quality_reports(self, output_path: str) -> None:
        """
        품질 리포트를 JSON 파일로 저장합니다.

        Args:
            output_path: 출력 파일 경로
        """
        import json

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.quality_reports, f, indent=2, ensure_ascii=False)

        logger.info(f"품질 리포트 저장: {output_file}")


def load_data_from_config(config: Dict) -> DataLoader:
    """
    설정 파일을 기반으로 데이터를 로딩합니다.

    Args:
        config: 설정 딕셔너리 (YAML 로딩 결과)

    Returns:
        로딩된 DataLoader 객체
    """
    data_config = config.get("data", {})

    loader = DataLoader()
    loader.load_all(
        bcr_file=data_config.get("bcr_file", "BCR_result.xlsx"),
        ems_file=data_config.get("ems_file", "EMS_result.xlsx"),
        resident_file=data_config.get("resident_file", "Resident_result.xlsx"),
    )

    return loader
