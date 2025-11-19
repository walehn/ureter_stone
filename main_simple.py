#!/usr/bin/env python3
"""
요관 결석 탐지 AI 성능 분석 - 통합 파이프라인 (Simple Version)

기존 실행 스크립트들을 순차적으로 호출하여 전체 분석을 수행합니다.

Usage:
    python main_simple.py [--skip-bootstrap] [--skip-visualization]
"""

import subprocess
import argparse
import sys
from pathlib import Path
from datetime import datetime
import time

class SimplePipeline:
    """간소화된 파이프라인: 기존 스크립트를 순차 실행"""

    def __init__(self, skip_bootstrap=False, skip_visualization=False):
        self.skip_bootstrap = skip_bootstrap
        self.skip_visualization = skip_visualization
        self.start_time = datetime.now()

        print("=" * 80)
        print("요관 결석 탐지 AI 성능 분석 - 통합 파이프라인")
        print("=" * 80)
        print(f"시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Bootstrap: {'SKIP' if skip_bootstrap else 'RUN'}")
        print(f"Visualization: {'SKIP' if skip_visualization else 'RUN'}")
        print("=" * 80)

    def run_script(self, script_name, description):
        """스크립트 실행"""
        print(f"\n{description}...")
        print("-" * 80)

        start = time.time()
        result = subprocess.run(['python3', script_name], capture_output=False)
        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"✗ 오류 발생: {script_name} 실행 실패 (exit code {result.returncode})")
            return False

        print(f"✓ 완료 ({elapsed:.1f}초)")
        return True

    def run(self):
        """전체 파이프라인 실행"""
        steps = [
            ('run_real_analysis.py', '[Step 1/6] Patient-level Metrics 계산'),
        ]

        if not self.skip_bootstrap:
            steps.append(('run_bootstrap_analysis.py', '[Step 2/6] Bootstrap Analysis (B=1000)'))

        steps.extend([
            ('run_gee_analysis.py', '[Step 3/6] GEE Analysis'),
            ('run_dca_analysis.py', '[Step 4/6] Decision Curve Analysis'),
            ('run_lesion_metrics.py', '[Step 5/6] Lesion-level Metrics'),
        ])

        if not self.skip_visualization:
            steps.append(('run_visualization.py', '[Step 6/6] Visualization'))

        steps.append(('run_reporting.py', '[Final] Report Generation'))

        # 각 스텝 실행
        for script, description in steps:
            if not self.run_script(script, description):
                print(f"\n파이프라인 중단: {script} 실패")
                return False

        # 완료 메시지
        end_time = datetime.now()
        elapsed = (end_time - self.start_time).total_seconds()

        print("\n" + "=" * 80)
        print("파이프라인 완료!")
        print("=" * 80)
        print(f"총 소요 시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")
        print(f"종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n결과 위치:")
        print(f"  - 전체 결과: results/")
        print(f"  - 최종 보고서: results/reports/supplement_full_report.md")
        print(f"  - 그래프: results/figures/")
        print("=" * 80)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='요관 결석 탐지 AI 성능 분석 - 통합 파이프라인 (Simple)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python main_simple.py                      # 전체 분석 실행
  python main_simple.py --skip-bootstrap     # Bootstrap 건너뛰기 (~5분 절약)
  python main_simple.py --skip-visualization # 시각화 건너뛰기
        """
    )

    parser.add_argument('--skip-bootstrap', action='store_true',
                        help='Bootstrap 분석 건너뛰기')
    parser.add_argument('--skip-visualization', action='store_true',
                        help='시각화 건너뛰기')

    args = parser.parse_args()

    pipeline = SimplePipeline(
        skip_bootstrap=args.skip_bootstrap,
        skip_visualization=args.skip_visualization
    )

    success = pipeline.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
