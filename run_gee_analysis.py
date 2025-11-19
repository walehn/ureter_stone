"""
실제 데이터로 FR-04 GEE Analysis 실행

BCR, EMS, Resident 각 리더별로 GEE 분석 수행.
Outcome: Correct classification (TP or TN = 1, FP or FN = 0)
"""

import openpyxl
from pathlib import Path
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.gee_analysis import GEEAnalyzer
from src.logger import setup_logger

logger = setup_logger("gee_analysis", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI GEE 분석 - Cluster-robust Inference")
print("=" * 80)


def load_reader_data_for_gee(filename, reader_type):
    """
    Excel 파일 로딩 및 GEE 분석용 형식으로 변환

    Outcome: Correct classification (TP or TN = 1, FP or FN = 0)
    Mode: 0 = unaided, 1 = assisted
    """
    wb = openpyxl.load_workbook(filename, data_only=True)
    ws = wb.active

    # Reader 타입에 따라 인덱스 설정
    if reader_type == 'Resident':
        pid_idx = 3
        result_unaided_idx = 19
        result_assisted_idx = 20
    else:  # BCR, EMS
        pid_idx = 2
        result_unaided_idx = 18
        result_assisted_idx = 19

    # 데이터 추출 (Row 5부터)
    data_combined = []

    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row or len(row) <= max(result_assisted_idx, result_unaided_idx):
            continue

        if row[pid_idx] is None:
            continue

        patient_id = str(row[pid_idx])
        result_unaided = row[result_unaided_idx]
        result_assisted = row[result_assisted_idx]

        # Result를 outcome (correct=1, incorrect=0)으로 변환
        def result_to_outcome(result_str):
            """
            TP, TN = Correct = 1
            FP, FN = Incorrect = 0
            """
            if result_str in ['TP', 'TN']:
                return 1
            elif result_str in ['FP', 'FN']:
                return 0
            else:
                return None

        # Unaided (mode=0)
        outcome_u = result_to_outcome(result_unaided)
        if outcome_u is not None:
            data_combined.append({
                'patient_id': patient_id,
                'outcome': outcome_u,
                'mode': 0,  # unaided
                'reader_id': 0  # placeholder
            })

        # Assisted (mode=1)
        outcome_a = result_to_outcome(result_assisted)
        if outcome_a is not None:
            data_combined.append({
                'patient_id': patient_id,
                'outcome': outcome_a,
                'mode': 1,  # assisted
                'reader_id': 0  # placeholder
            })

    n_patients = len(set(r['patient_id'] for r in data_combined)) // 2  # unaided + assisted

    logger.info(f"[{reader_type}] 데이터 로딩 완료:")
    logger.info(f"  Total records: {len(data_combined)} (unaided + assisted)")
    logger.info(f"  Unique patients: {n_patients}")
    logger.info(f"  Outcome distribution: {sum(r['outcome'] for r in data_combined)}/{len(data_combined)} correct")

    return data_combined


# 3개 리더 데이터 로딩 및 분석
readers = {
    'BCR': 'BCR_result.xlsx',
    'EMS': 'EMS_result.xlsx',
    'Resident': 'Resident_result.xlsx'
}

all_results = {}

print("\n[1] GEE 분석 실행...")
print("-" * 80)

for reader_name, filename in readers.items():
    try:
        # 데이터 로딩
        data = load_reader_data_for_gee(filename, reader_name)

        # GEE 분석 실행
        print(f"\n{'='*80}")
        print(f"[{reader_name}] GEE Analysis")
        print(f"{'='*80}")

        analyzer = GEEAnalyzer(max_iter=100, tol=1e-6)

        results = analyzer.fit(data, include_reader=False)

        all_results[reader_name] = {
            'analyzer': analyzer,
            'results': results
        }

        # 결과 저장
        output_dir = Path("results") / "gee" / reader_name
        analyzer.export_results(output_dir)

        print(f"\n✓ {reader_name} GEE 분석 완료!")
        print(f"  결과 저장: {output_dir}/")

    except Exception as e:
        logger.error(f"✗ {reader_name} 처리 실패: {e}")
        import traceback
        traceback.print_exc()

# 종합 요약
print("\n" + "=" * 80)
print("[2] 전체 리더 GEE 결과 요약")
print("=" * 80)

for reader_name, data in all_results.items():
    results = data['results']

    print(f"\n[{reader_name}]")
    print("-" * 80)

    mode_coef = results['coefficients']['Mode (Assisted vs Unaided)']

    print(f"  AI Assistance Effect:")
    print(f"    Beta:      {mode_coef['beta']:+.4f} (SE: {mode_coef['se_robust']:.4f})")
    print(f"    z-score:   {mode_coef['z']:+.3f}")
    print(f"    p-value:   {mode_coef['p_value']:.4f} {'***' if mode_coef['p_value'] < 0.001 else '**' if mode_coef['p_value'] < 0.01 else '*' if mode_coef['p_value'] < 0.05 else ''}")
    print(f"    OR:        {mode_coef['OR']:.3f} (95% CI: [{mode_coef['OR_ci_lower']:.3f}, {mode_coef['OR_ci_upper']:.3f}])")

    if mode_coef['OR'] > 1:
        direction = "increases"
        pct = (mode_coef['OR'] - 1) * 100
    else:
        direction = "decreases"
        pct = (1 - mode_coef['OR']) * 100

    print(f"    → AI assistance {direction} odds of correct classification by {pct:.1f}%")

print("\n" + "=" * 80)
print("GEE 분석 완료!")
print("=" * 80)
print(f"\n📊 주요 발견사항:")
print(f"  - Cluster-robust inference (환자 내 상관관계 고려)")
print(f"  - Exchangeable correlation structure")
print(f"  - Sandwich (robust) standard errors")
print(f"  - 결과 저장: results/gee/")
