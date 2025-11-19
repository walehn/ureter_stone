"""
요관 결석 탐지 AI 성능 분석 시스템

AI object detection 기반 의학 연구의 통계 분석을 자동화합니다.
- 환자단위 성능 분석 (Primary)
- 병변단위 성능 분석 (Secondary)
- Cluster-robust bootstrap
- GEE robust inference
- Decision Curve Analysis
"""

__version__ = "1.0.0"
__author__ = "Medical AI Research Team"

# 모듈 버전 정보
MODULES = {
    "data_loader": "FR-01: 데이터 입력 처리",
    "patient_metrics": "FR-02: 환자단위 지표 계산",
    "bootstrap": "FR-03: Cluster-robust Bootstrap",
    "gee_analysis": "FR-04: GEE Robust Analysis",
    "dca": "FR-05: Decision Curve Analysis",
    "lesion_metrics": "FR-06: Lesion-level Metrics",
    "visualization": "FR-07: 시각화 및 그래프",
    "reporter": "FR-08: Reporting Package",
}
