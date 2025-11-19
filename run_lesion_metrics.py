"""
실제 데이터로 FR-06 Lesion Metrics 실행

BCR, EMS, Resident 각 리더별로 병변 단위 성능 분석.
Precision, Recall, F1 Score 계산.
"""

import openpyxl
from pathlib import Path
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.lesion_metrics import LesionMetricsCalculator
from src.logger import setup_logger

logger = setup_logger("lesion_metrics_analysis", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI Lesion-level Performance Metrics")
print("=" * 80)


def load_lesion_counts(filename, reader_type):
    """
    Excel 파일에서 병변 단위 TP, FP, FN 집계

    BCR/EMS:
    - Col 4-6: Per lesion without AI (TP, FP, FN)
    - Col 7-9: Per lesion with AI (TP, FP, FN)

    Resident:
    - Col 5-7: Per lesion without AI (TP, FP, FN)
    - Col 8-10: Per lesion with AI (TP, FP, FN)

    Returns:
        (lesion_counts_unaided, lesion_counts_assisted)
    """
    wb = openpyxl.load_workbook(filename, data_only=True)
    ws = wb.active

    # Reader 타입에 따라 인덱스 설정
    if reader_type == 'Resident':
        # Resident는 size 컬럼 때문에 1칸 밀림
        tp_unaided_idx = 5
        fp_unaided_idx = 6
        fn_unaided_idx = 7
        tp_assisted_idx = 8
        fp_assisted_idx = 9
        fn_assisted_idx = 10
    else:  # BCR, EMS
        tp_unaided_idx = 4
        fp_unaided_idx = 5
        fn_unaided_idx = 6
        tp_assisted_idx = 7
        fp_assisted_idx = 8
        fn_assisted_idx = 9

    # 병변 카운트 초기화
    lesion_counts_unaided = {'TP': 0, 'FP': 0, 'FN': 0}
    lesion_counts_assisted = {'TP': 0, 'FP': 0, 'FN': 0}

    # 데이터 집계 (Row 5부터)
    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row:
            continue

        # Unaided
        tp_u = row[tp_unaided_idx] if row[tp_unaided_idx] is not None else 0
        fp_u = row[fp_unaided_idx] if row[fp_unaided_idx] is not None else 0
        fn_u = row[fn_unaided_idx] if row[fn_unaided_idx] is not None else 0

        # 숫자로 변환 (P/N 같은 문자열 제외)
        try:
            lesion_counts_unaided['TP'] += int(tp_u)
            lesion_counts_unaided['FP'] += int(fp_u)
            lesion_counts_unaided['FN'] += int(fn_u)
        except (ValueError, TypeError):
            pass

        # Assisted
        tp_a = row[tp_assisted_idx] if row[tp_assisted_idx] is not None else 0
        fp_a = row[fp_assisted_idx] if row[fp_assisted_idx] is not None else 0
        fn_a = row[fn_assisted_idx] if row[fn_assisted_idx] is not None else 0

        try:
            lesion_counts_assisted['TP'] += int(tp_a)
            lesion_counts_assisted['FP'] += int(fp_a)
            lesion_counts_assisted['FN'] += int(fn_a)
        except (ValueError, TypeError):
            pass

    logger.info(f"[{reader_type}] Lesion counts 로딩 완료:")
    logger.info(f"  Unaided: TP={lesion_counts_unaided['TP']}, FP={lesion_counts_unaided['FP']}, FN={lesion_counts_unaided['FN']}")
    logger.info(f"  Assisted: TP={lesion_counts_assisted['TP']}, FP={lesion_counts_assisted['FP']}, FN={lesion_counts_assisted['FN']}")

    return lesion_counts_unaided, lesion_counts_assisted


# 3개 리더 데이터 로딩 및 분석
readers = {
    'BCR': 'BCR_result.xlsx',
    'EMS': 'EMS_result.xlsx',
    'Resident': 'Resident_result.xlsx'
}

all_results = {}

print("\n[1] Lesion-level Metrics 분석 실행...")
print("-" * 80)

for reader_name, filename in readers.items():
    try:
        # Lesion counts 로딩
        lesion_counts_unaided, lesion_counts_assisted = load_lesion_counts(filename, reader_name)

        # Lesion Metrics 분석 실행
        print(f"\n{'='*80}")
        print(f"[{reader_name}] Lesion-level Metrics")
        print(f"{'='*80}")

        calculator = LesionMetricsCalculator()

        results = calculator.compare_strategies(lesion_counts_assisted, lesion_counts_unaided)

        all_results[reader_name] = {
            'calculator': calculator,
            'results': results
        }

        # 결과 저장
        output_dir = Path("results") / "lesion_metrics" / reader_name
        calculator.export_results(output_dir)

        print(f"\n✓ {reader_name} Lesion Metrics 분석 완료!")
        print(f"  결과 저장: {output_dir}/")

    except Exception as e:
        logger.error(f"✗ {reader_name} 처리 실패: {e}")
        import traceback
        traceback.print_exc()

# 종합 요약
print("\n" + "=" * 80)
print("[2] 전체 리더 Lesion Metrics 결과 요약")
print("=" * 80)

for reader_name, data in all_results.items():
    results = data['results']

    print(f"\n[{reader_name}]")
    print("-" * 80)

    # Assisted vs Unaided 비교
    m_a = results['assisted']
    m_u = results['unaided']
    delta = results['delta']

    print(f"  Assisted (With AI):")
    print(f"    Precision: {m_a['precision']:.4f} ({m_a['precision']*100:.2f}%)")
    print(f"    Recall:    {m_a['recall']:.4f} ({m_a['recall']*100:.2f}%)")
    print(f"    F1 Score:  {m_a['f1_score']:.4f} ({m_a['f1_score']*100:.2f}%)")

    print(f"\n  Unaided (Without AI):")
    print(f"    Precision: {m_u['precision']:.4f} ({m_u['precision']*100:.2f}%)")
    print(f"    Recall:    {m_u['recall']:.4f} ({m_u['recall']*100:.2f}%)")
    print(f"    F1 Score:  {m_u['f1_score']:.4f} ({m_u['f1_score']*100:.2f}%)")

    print(f"\n  Δ (Assisted - Unaided):")
    print(f"    Δ Precision: {delta['precision']:+.4f} ({delta['precision']*100:+.2f}%)")
    print(f"    Δ Recall:    {delta['recall']:+.4f} ({delta['recall']*100:+.2f}%)")
    print(f"    Δ F1 Score:  {delta['f1_score']:+.4f} ({delta['f1_score']*100:+.2f}%)")

    # Trade-off 분석
    if delta['precision'] > 0 and delta['recall'] < 0:
        print(f"    → Trade-off: ↑ Precision, ↓ Recall")
    elif delta['precision'] < 0 and delta['recall'] > 0:
        print(f"    → Trade-off: ↓ Precision, ↑ Recall")
    elif delta['precision'] > 0 and delta['recall'] > 0:
        print(f"    → Win-win: ↑ Both Precision and Recall!")
    else:
        print(f"    → Caution: ↓ Both metrics")

print("\n" + "=" * 80)
print("Lesion Metrics 분석 완료!")
print("=" * 80)
print(f"\n📊 주요 발견사항:")
print(f"  - Precision: 찾은 병변 중 정확한 비율")
print(f"  - Recall: 실제 병변 중 찾은 비율")
print(f"  - F1 Score: Precision과 Recall의 조화평균")
print(f"  - 결과 저장: results/lesion_metrics/")
