"""
전체 분석 결과를 통합하여 Supplement-ready 보고서 생성

모든 분석 결과(Patient-level, Bootstrap, GEE, DCA, Lesion-level)를
하나의 통합 보고서로 생성합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.reporter import SupplementReporter
from src.logger import setup_logger

logger = setup_logger("reporting", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI - Supplement-ready 통합 보고서 생성")
print("=" * 80)

# Reporter 초기화
reporter = SupplementReporter(results_dir=Path("results"))

# 전체 보고서 생성
report_path = reporter.generate_full_report()

print(f"\n{'=' * 80}")
print("보고서 생성 완료!")
print(f"{'=' * 80}\n")

print("📄 생성된 파일:")
print(f"  1. {report_path}")
print(f"     → Markdown 형식 전체 보고서 (Supplement-ready)")
print(f"  2. results/reports/integrated_results.json")
print(f"     → JSON 형식 통합 데이터")

print(f"\n📊 포함된 내용:")
print("  - Executive Summary: 주요 발견사항 요약")
print("  - Table 1: Patient-level Performance Metrics")
print("  - Table 2: Bootstrap 95% Confidence Intervals")
print("  - Table 3: GEE Analysis Results")
print("  - Table 4: Decision Curve Analysis Summary")
print("  - Table 5: Lesion-level Detection Performance")
print("  - Statistical Methods: 분석 방법론 상세 기술")
print("  - Figures Reference: 그래프 목록 및 설명")

print(f"\n✨ 다음 단계:")
print("  - 보고서 검토 및 논문 Supplement에 통합")
print("  - 필요시 테이블/그래프 추가 편집")
print("  - Phase 11: Main Pipeline 구현으로 전체 분석 자동화")
