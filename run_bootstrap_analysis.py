"""
실제 데이터로 FR-03 Bootstrap Analysis 실행

BCR, EMS, Resident 각 리더별로 patient-level bootstrap 분석 수행
"""

import openpyxl
from pathlib import Path
import sys
import csv

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.bootstrap import BootstrapAnalyzer
from src.logger import setup_logger

logger = setup_logger("bootstrap_analysis", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI Bootstrap 분석 - Patient-level Cluster-robust")
print("=" * 80)


def load_reader_data_with_conversion(filename, reader_type):
    """
    Excel 파일 로딩 및 bootstrap 분석용 형식으로 변환

    Result 컬럼('TP', 'FP', 'TN', 'FN')을 ground_truth, prediction으로 변환:
    - TP: ground_truth=1, prediction=1
    - FP: ground_truth=0, prediction=1
    - FN: ground_truth=1, prediction=0
    - TN: ground_truth=0, prediction=0
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
    unaided_data = []
    assisted_data = []

    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row or len(row) <= max(result_assisted_idx, result_unaided_idx):
            continue

        if row[pid_idx] is None:
            continue

        patient_id = str(row[pid_idx])
        result_unaided = row[result_unaided_idx]
        result_assisted = row[result_assisted_idx]

        # Result를 ground_truth, prediction으로 변환
        def convert_result(result_str):
            """Result 문자열을 (ground_truth, prediction) 튜플로 변환"""
            if result_str == 'TP':
                return (1, 1)
            elif result_str == 'FP':
                return (0, 1)
            elif result_str == 'FN':
                return (1, 0)
            elif result_str == 'TN':
                return (0, 0)
            else:
                return (None, None)

        # Unaided 변환
        gt_u, pred_u = convert_result(result_unaided)
        if gt_u is not None:
            unaided_data.append({
                'patient_id': patient_id,
                'ground_truth': gt_u,
                'prediction': pred_u
            })

        # Assisted 변환
        gt_a, pred_a = convert_result(result_assisted)
        if gt_a is not None:
            assisted_data.append({
                'patient_id': patient_id,
                'ground_truth': gt_a,
                'prediction': pred_a
            })

    # 데이터는 리스트 그대로 반환 (pandas 불필요)
    n_patients_unaided = len(set(r['patient_id'] for r in unaided_data))
    n_patients_assisted = len(set(r['patient_id'] for r in assisted_data))

    logger.info(f"[{reader_type}] 데이터 로딩 완료:")
    logger.info(f"  Unaided: {len(unaided_data)}개 레코드, {n_patients_unaided}명 환자")
    logger.info(f"  Assisted: {len(assisted_data)}개 레코드, {n_patients_assisted}명 환자")

    return unaided_data, assisted_data


# 3개 리더 데이터 로딩
readers = {
    'BCR': 'BCR_result.xlsx',
    'EMS': 'EMS_result.xlsx',
    'Resident': 'Resident_result.xlsx'
}

all_results = {}

print("\n[1] 데이터 로딩 및 변환...")
print("-" * 80)

for reader_name, filename in readers.items():
    try:
        data_unaided, data_assisted = load_reader_data_with_conversion(filename, reader_name)

        # Bootstrap 분석 실행
        print(f"\n[2] Bootstrap 분석 실행: {reader_name}")
        print("-" * 80)

        analyzer = BootstrapAnalyzer(
            n_iterations=1000,
            confidence_level=0.95,
            random_seed=42
        )

        results = analyzer.run_comparison(
            data_assisted=data_assisted,
            data_unaided=data_unaided
        )

        all_results[reader_name] = {
            'analyzer': analyzer,
            'results': results
        }

        # 결과 저장
        output_dir = Path("results") / "bootstrap" / reader_name
        analyzer.export_results(output_dir)

        print(f"\n✓ {reader_name} Bootstrap 분석 완료!")
        print(f"  결과 저장: {output_dir}/")

    except Exception as e:
        logger.error(f"✗ {reader_name} 처리 실패: {e}")
        import traceback
        traceback.print_exc()

# 종합 요약
print("\n" + "=" * 80)
print("[3] 전체 리더 비교 요약")
print("=" * 80)

summary_rows = []

for reader_name, data in all_results.items():
    results = data['results']

    print(f"\n[{reader_name}]")
    print("-" * 80)

    for metric_name in ['sensitivity', 'specificity', 'ppv', 'npv']:
        delta_data = results['delta']['metrics'][metric_name]
        mean_delta = delta_data['mean']
        ci_lower = delta_data['ci_lower']
        ci_upper = delta_data['ci_upper']
        significant = delta_data['significant']
        sig_symbol = " **" if significant else ""

        print(f"  Δ {metric_name.upper():12s}: {mean_delta:+.3f} "
              f"(95% CI: [{ci_lower:+.3f}, {ci_upper:+.3f}]){sig_symbol}")

        summary_rows.append({
            'Reader': reader_name,
            'Metric': metric_name.upper(),
            'Delta': mean_delta,
            'CI_Lower': ci_lower,
            'CI_Upper': ci_upper,
            'Significant': 'Yes' if significant else 'No'
        })

# 전체 요약 테이블 저장 (pandas 없이)
summary_file = Path("results") / "bootstrap" / "all_readers_summary.csv"
summary_file.parent.mkdir(parents=True, exist_ok=True)

with open(summary_file, 'w', newline='', encoding='utf-8') as f:
    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

print(f"\n✓ 전체 요약 저장: {summary_file}")

print("\n" + "=" * 80)
print("Bootstrap 분석 완료!")
print("=" * 80)
print(f"\n📊 주요 발견사항:")
print(f"  - Bootstrap iterations: 1000회")
print(f"  - Confidence level: 95%")
print(f"  - Resampling 단위: Patient-level (cluster-robust)")
print(f"  - 결과 저장: results/bootstrap/")
