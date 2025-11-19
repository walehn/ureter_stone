"""
상수 정의 모듈

프로젝트 전반에서 사용되는 상수들을 중앙에서 관리합니다.
"""

# 리더 타입
READER_TYPES = {
    "BCR": "Board-certified Radiologist",  # 영상의학전문의
    "EMS": "Emergency Medicine Specialist",  # 응급의학과전문의
    "RESIDENT": "Radiology Resident",  # 영상의학과전공의
}

# 모드 (AI 보조 여부)
MODE_ASSISTED = "assisted"
MODE_UNAIDED = "unaided"

# 메트릭 이름
PATIENT_METRICS = ["sensitivity", "specificity", "ppv", "npv"]
LESION_METRICS = ["precision", "recall", "f1", "map@0.5", "map@0.45"]

# Confusion Matrix 라벨
CM_LABELS = {
    "TP": "True Positive",
    "FP": "False Positive",
    "TN": "True Negative",
    "FN": "False Negative",
}

# 그래프 제목 (한국어)
FIGURE_TITLES = {
    "bootstrap_dist": "Bootstrap Distribution",
    "dca": "Decision Curve Analysis",
    "pr_curve": "Precision-Recall Curve",
    "confusion_matrix": "Confusion Matrix",
    "comparison": "Assisted vs Unaided Comparison",
}

# 테이블 이름
TABLE_NAMES = {
    "patient_confusion": "Patient-level Confusion Matrix",
    "bootstrap_ci": "Bootstrap 95% Confidence Intervals",
    "dca_summary": "Decision Curve Analysis Summary",
    "lesion_metrics": "Lesion-level Detection Metrics",
}

# 파일 확장자
OUTPUT_FORMATS = {
    "table": ["csv", "md"],  # Markdown
    "figure": ["png"],
    "data": ["json"],
}

# Bootstrap 기본 설정
DEFAULT_BOOTSTRAP_ITERATIONS = 1000
DEFAULT_CONFIDENCE_LEVEL = 0.95

# DCA threshold 범위
DEFAULT_DCA_THRESHOLD_MIN = 0.05
DEFAULT_DCA_THRESHOLD_MAX = 0.25

# 성능 요구사항 (초 단위)
PERFORMANCE_REQUIREMENTS = {
    "bootstrap_1000": 300,  # 5분
    "gee_fitting": 1,
    "dca_curve": 1,
    "total_pipeline": 600,  # 10분
}

# Excel 컬럼명 매핑 (실제 데이터에 맞게 조정 필요)
EXCEL_COLUMNS = {
    "patient_id": "Patient_ID",
    "lesion_id": "Lesion_ID",
    "reader_id": "Reader_ID",
    "mode": "Mode",  # assisted / unaided
    "prediction": "Prediction",
    "ground_truth": "Ground_Truth",
    "bbox": "BBox",  # Bounding box coordinates
}
