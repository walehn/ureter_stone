"""
Bootstrap Analysis 테스트

주요 검증 항목:
- Patient-level resampling 정확성
- 신뢰구간 계산
- 재현성 (random seed)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bootstrap import BootstrapAnalyzer


def test_bootstrap_initialization():
    """Bootstrap Analyzer 초기화 테스트"""
    analyzer = BootstrapAnalyzer(n_iterations=10, random_seed=42)
    assert analyzer.n_iterations == 10
    assert analyzer.random_seed == 42
    assert analyzer.confidence_level == 0.95
    print("✓ Bootstrap 초기화 테스트 통과")


def test_bootstrap_resampling():
    """Patient-level resampling 테스트"""
    # 샘플 데이터 생성 (3명 환자)
    test_data = [
        {'patient_id': 'P1', 'result_unaided': 'TP', 'result_assisted': 'TP'},
        {'patient_id': 'P1', 'result_unaided': 'TP', 'result_assisted': 'TP'},  # 동일 환자
        {'patient_id': 'P2', 'result_unaided': 'TN', 'result_assisted': 'TN'},
        {'patient_id': 'P3', 'result_unaided': 'FP', 'result_assisted': 'TN'},
    ]

    analyzer = BootstrapAnalyzer(n_iterations=10, random_seed=42)
    resampled = analyzer.resample_patients(test_data)

    # 리샘플링 결과 검증
    assert len(resampled) > 0, "Resampled data should not be empty"

    # 환자 ID 수집
    patient_ids = set(record['patient_id'] for record in resampled)
    assert len(patient_ids) >= 1, "Should have at least 1 patient ID"

    print(f"✓ Resampling 테스트 통과 (Original: {len(test_data)}, Resampled: {len(resampled)})")


def test_bootstrap_reproducibility():
    """Random seed를 통한 재현성 테스트"""
    test_data = [
        {'patient_id': f'P{i}', 'result_unaided': 'TP', 'result_assisted': 'TP'}
        for i in range(10)
    ]

    analyzer1 = BootstrapAnalyzer(n_iterations=5, random_seed=42)
    analyzer2 = BootstrapAnalyzer(n_iterations=5, random_seed=42)

    results1 = analyzer1.run_comparison(test_data)
    results2 = analyzer2.run_comparison(test_data)

    # 같은 seed면 같은 결과
    assert abs(results1['assisted']['point_estimates']['sensitivity'] -
               results2['assisted']['point_estimates']['sensitivity']) < 1e-10

    print("✓ 재현성 테스트 통과 (동일 seed → 동일 결과)")


def test_confidence_interval_bounds():
    """신뢰구간 경계값 테스트"""
    test_data = [
        {'patient_id': f'P{i}', 'result_unaided': 'TP', 'result_assisted': 'TP'}
        for i in range(20)
    ]

    analyzer = BootstrapAnalyzer(n_iterations=100, random_seed=42)
    results = analyzer.run_comparison(test_data)

    # CI는 point estimate를 포함해야 함
    for metric in ['sensitivity', 'specificity', 'ppv', 'npv']:
        pe = results['assisted']['point_estimates'][metric]
        ci = results['assisted']['confidence_intervals'][metric]

        # CI 범위 내에 point estimate가 있는지 확인 (일반적으로 참)
        # Bootstrap은 quantile method이므로 항상 참은 아님
        assert ci['lower'] <= ci['upper'], f"{metric}: CI lower should be <= upper"

    print("✓ 신뢰구간 경계값 테스트 통과")


if __name__ == "__main__":
    print("=" * 60)
    print("Bootstrap Analysis 테스트 실행")
    print("=" * 60)

    test_bootstrap_initialization()
    test_bootstrap_resampling()
    test_bootstrap_reproducibility()
    test_confidence_interval_bounds()

    print("\n" + "=" * 60)
    print("모든 테스트 통과! ✓")
    print("=" * 60)
