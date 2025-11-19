"""
실제 데이터로 FR-05 Decision Curve Analysis 실행

BCR, EMS, Resident 각 리더별로 DCA 수행.
Net benefit을 통해 AI 보조의 임상적 유용성 평가.
"""

import openpyxl
from pathlib import Path
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.dca import DecisionCurveAnalyzer
from src.logger import setup_logger

logger = setup_logger("dca_analysis", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI Decision Curve Analysis - Clinical Utility")
print("=" * 80)


def load_confusion_matrices(filename, reader_type):
    """
    Excel 파일에서 confusion matrix 추출

    Returns:
        (cm_unaided, cm_assisted): Confusion matrices
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

    # Confusion matrices 초기화
    cm_unaided = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
    cm_assisted = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}

    # 데이터 추출 (환자 단위로 집계)
    patient_results = {}

    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row or len(row) <= max(result_assisted_idx, result_unaided_idx):
            continue

        if row[pid_idx] is None:
            continue

        patient_id = str(row[pid_idx])
        result_unaided = row[result_unaided_idx]
        result_assisted = row[result_assisted_idx]

        # 환자당 하나의 결과만 (첫 번째)
        if patient_id not in patient_results:
            patient_results[patient_id] = {
                'unaided': result_unaided,
                'assisted': result_assisted
            }

    # Confusion matrix 계산
    for patient_id, results in patient_results.items():
        # Unaided
        if results['unaided'] in cm_unaided:
            cm_unaided[results['unaided']] += 1

        # Assisted
        if results['assisted'] in cm_assisted:
            cm_assisted[results['assisted']] += 1

    logger.info(f"[{reader_type}] Confusion matrices 로딩 완료:")
    logger.info(f"  Unaided: TP={cm_unaided['TP']}, FP={cm_unaided['FP']}, FN={cm_unaided['FN']}, TN={cm_unaided['TN']}")
    logger.info(f"  Assisted: TP={cm_assisted['TP']}, FP={cm_assisted['FP']}, FN={cm_assisted['FN']}, TN={cm_assisted['TN']}")

    return cm_unaided, cm_assisted


# 3개 리더 데이터 로딩 및 분석
readers = {
    'BCR': 'BCR_result.xlsx',
    'EMS': 'EMS_result.xlsx',
    'Resident': 'Resident_result.xlsx'
}

all_results = {}

print("\n[1] Decision Curve Analysis 실행...")
print("-" * 80)

for reader_name, filename in readers.items():
    try:
        # Confusion matrices 로딩
        cm_unaided, cm_assisted = load_confusion_matrices(filename, reader_name)

        # DCA 분석 실행
        print(f"\n{'='*80}")
        print(f"[{reader_name}] Decision Curve Analysis")
        print(f"{'='*80}")

        analyzer = DecisionCurveAnalyzer(
            threshold_min=0.05,
            threshold_max=0.25,
            n_thresholds=50
        )

        results = analyzer.compare_strategies(cm_assisted, cm_unaided)

        all_results[reader_name] = {
            'analyzer': analyzer,
            'results': results
        }

        # 결과 저장
        output_dir = Path("results") / "dca" / reader_name
        analyzer.export_results(output_dir)

        print(f"\n✓ {reader_name} DCA 분석 완료!")
        print(f"  결과 저장: {output_dir}/")

    except Exception as e:
        logger.error(f"✗ {reader_name} 처리 실패: {e}")
        import traceback
        traceback.print_exc()

# 종합 요약
print("\n" + "=" * 80)
print("[2] 전체 리더 DCA 결과 요약")
print("=" * 80)

import numpy as np

for reader_name, data in all_results.items():
    results = data['results']

    print(f"\n[{reader_name}]")
    print("-" * 80)

    # Delta net benefit 분석
    delta_nb = results['delta_net_benefit']
    thresholds = results['thresholds']

    positive_count = sum(1 for d in delta_nb if d > 0)
    positive_pct = positive_count / len(delta_nb) * 100

    max_delta_idx = np.argmax(np.abs(delta_nb))
    max_delta = delta_nb[max_delta_idx]
    max_threshold = thresholds[max_delta_idx]

    print(f"  Clinical Utility:")
    print(f"    AI is better: {positive_count}/{len(delta_nb)} thresholds ({positive_pct:.1f}%)")
    print(f"    Max Δ NB: {max_delta:+.4f} at threshold={max_threshold:.3f}")

    # 주요 threshold에서의 net benefit
    print(f"\n  Net Benefit at Key Thresholds:")
    for target_threshold in [0.05, 0.10, 0.15, 0.20, 0.25]:
        idx = np.argmin(np.abs(np.array(thresholds) - target_threshold))
        nb_assisted = results['assisted']['net_benefit_model'][idx]
        nb_unaided = results['unaided']['net_benefit_model'][idx]
        delta = delta_nb[idx]
        better = "AI better" if delta > 0 else "Unaided better" if delta < 0 else "Equal"

        print(f"    pt={target_threshold:.2f}: Assisted={nb_assisted:.4f}, Unaided={nb_unaided:.4f}, "
              f"Δ={delta:+.4f} ({better})")

print("\n" + "=" * 80)
print("DCA 분석 완료!")
print("=" * 80)
print(f"\n📊 주요 발견사항:")
print(f"  - Net Benefit: 진단의 이득 - 손해")
print(f"  - Threshold: 치료 선택 최소 확률 (0.05 ~ 0.25)")
print(f"  - Clinical utility: AI의 실제 임상적 유용성 평가")
print(f"  - 결과 저장: results/dca/")
