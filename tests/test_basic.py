"""
기본 모듈 테스트

간단한 유닛 테스트로 핵심 기능 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """모듈 import 테스트"""
    try:
        from src.bootstrap import BootstrapAnalyzer
        from src.gee_analysis import GEEAnalyzer
        from src.dca import DecisionCurveAnalyzer
        from src.lesion_metrics import LesionMetricsCalculator
        from src.visualization import Visualizer
        from src.reporter import SupplementReporter
        print("✓ 모든 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"✗ Import 실패: {e}")
        return False


def test_bootstrap_init():
    """Bootstrap 초기화 테스트"""
    from src.bootstrap import BootstrapAnalyzer

    analyzer = BootstrapAnalyzer(n_iterations=10, random_seed=42)
    assert analyzer.n_iterations == 10
    assert analyzer.random_seed == 42
    print("✓ Bootstrap 초기화 성공")
    return True


def test_lesion_metrics_calculation():
    """Lesion Metrics 계산 테스트"""
    from src.lesion_metrics import LesionMetricsCalculator

    calc = LesionMetricsCalculator()

    # Precision, Recall, F1 계산
    result = calc.calculate_metrics(tp=80, fp=20, fn=20)

    assert result['precision'] == 0.8, f"Expected 0.8, got {result['precision']}"
    assert result['recall'] == 0.8, f"Expected 0.8, got {result['recall']}"
    assert abs(result['f1_score'] - 0.8) < 0.001, f"Expected ~0.8, got {result['f1_score']}"

    print(f"✓ Lesion Metrics 계산 검증: Precision={result['precision']}, Recall={result['recall']}, F1={result['f1_score']}")
    return True


def test_dca_init():
    """DCA 초기화 테스트"""
    from src.dca import DecisionCurveAnalyzer

    analyzer = DecisionCurveAnalyzer(threshold_min=0.05, threshold_max=0.25, n_thresholds=50)
    assert analyzer.threshold_min == 0.05
    assert analyzer.threshold_max == 0.25
    assert analyzer.n_thresholds == 50

    print(f"✓ DCA 초기화 성공: {len(analyzer.thresholds)} thresholds")
    return True


def test_gee_init():
    """GEE 초기화 테스트"""
    from src.gee_analysis import GEEAnalyzer

    analyzer = GEEAnalyzer()
    # GEE analyzer가 정상적으로 초기화되었는지만 확인
    assert analyzer is not None

    print("✓ GEE Analyzer 초기화 성공")
    return True


def test_visualizer_init():
    """Visualizer 초기화 테스트"""
    from src.visualization import Visualizer

    viz = Visualizer(dpi=300, figsize=(10, 6))
    assert viz.dpi == 300
    assert viz.figsize == (10, 6)

    print("✓ Visualizer 초기화 성공")
    return True


def test_reporter_init():
    """Reporter 초기화 테스트"""
    from src.reporter import SupplementReporter

    reporter = SupplementReporter(results_dir=Path("results"))
    assert reporter.results_dir == Path("results")

    print("✓ SupplementReporter 초기화 성공")
    return True


def run_all_tests():
    """모든 테스트 실행"""
    tests = [
        ("Import 테스트", test_imports),
        ("Bootstrap 초기화", test_bootstrap_init),
        ("Lesion Metrics 계산", test_lesion_metrics_calculation),
        ("DCA 초기화", test_dca_init),
        ("GEE 초기화", test_gee_init),
        ("Visualizer 초기화", test_visualizer_init),
        ("Reporter 초기화", test_reporter_init),
    ]

    print("=" * 70)
    print("기본 모듈 테스트 실행")
    print("=" * 70)

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 테스트 실패: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"테스트 결과: {passed}개 성공, {failed}개 실패")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
