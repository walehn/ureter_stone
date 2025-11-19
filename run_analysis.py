"""
실제 데이터로 FR-01, FR-02 실행 스크립트

BCR, EMS, Resident 3개 리더의 결과를 분석합니다.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.logger import setup_logger
from src.data_loader import DataLoader
from src.patient_metrics import PatientMetricsCalculator

# 로거 설정
logger = setup_logger("analysis", level="INFO")

print("=" * 80)
print("요관 결석 탐지 AI 성능 분석 - 실제 데이터 분석")
print("=" * 80)

# 설정 파일 로딩
print("\n[1] 설정 파일 로딩...")
config_path = Path(__file__).parent / "config" / "analysis_config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(f"✓ 설정 로딩 완료: Bootstrap {config['analysis']['bootstrap']['n_iterations']}회")

# FR-01: 데이터 로딩
print("\n[2] FR-01: 데이터 로딩 및 검증...")
print("-" * 80)

loader = DataLoader()

try:
    # 3개 리더 데이터 로딩
    data = loader.load_all(
        bcr_file="BCR_result.xlsx",
        ems_file="EMS_result.xlsx",
        resident_file="Resident_result.xlsx"
    )

    print("\n✓ 데이터 로딩 성공!")
    print(f"  총 {len(data)}개 리더 데이터 로딩됨")

    # 각 리더별 요약
    print("\n📊 리더별 데이터 요약:")
    for reader_type, df in data.items():
        print(f"\n  [{reader_type}] {loader.quality_reports[reader_type]['reader_description']}")
        print(f"    - 총 레코드 수: {len(df):,}개")
        print(f"    - 컬럼 수: {len(df.columns)}개")
        print(f"    - 컬럼 목록: {', '.join(df.columns.tolist()[:5])}...")

        # 결측치 정보
        missing_info = loader.quality_reports[reader_type]['missing_values']
        if missing_info['missing_by_column']:
            print(f"    ⚠ 결측치: {missing_info['missing_by_column']}")
        else:
            print(f"    ✓ 결측치 없음")

    # 데이터 샘플 출력
    print("\n📋 BCR 데이터 샘플 (첫 3행):")
    print(data['BCR'].head(3).to_string())

except Exception as e:
    print(f"\n✗ 데이터 로딩 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# FR-02: 환자단위 지표 계산
print("\n" + "=" * 80)
print("[3] FR-02: 환자단위 성능 지표 계산")
print("=" * 80)

# 데이터 결합
try:
    combined_data = loader.get_combined_data()
    print(f"\n✓ 데이터 결합 완료: {len(combined_data):,}개 레코드")
    print(f"  컬럼: {combined_data.columns.tolist()}")

    # 컬럼 매핑 확인 및 조정 (실제 데이터 구조에 맞게)
    print("\n🔍 데이터 구조 분석 중...")

    # 실제 데이터에 필요한 컬럼이 있는지 확인
    required_cols = ['patient_id', 'mode', 'ground_truth', 'prediction']

    # 데이터 샘플로 구조 파악
    print("\n📊 결합 데이터 샘플:")
    print(combined_data.head(3).to_string())

    print("\n⚠ 실제 데이터 구조를 확인해야 합니다.")
    print("   현재 코드는 다음 컬럼을 기대합니다:")
    print(f"   - patient_id: 환자 ID")
    print(f"   - mode: assisted 또는 unaided")
    print(f"   - ground_truth: 실제 병변 유무 (0 or 1)")
    print(f"   - prediction: 예측 결과 (0 or 1)")

    # 컬럼 이름 확인
    actual_cols = combined_data.columns.tolist()
    print(f"\n   실제 컬럼: {actual_cols}")

    # 필요한 컬럼이 있는지 확인
    has_required = all(col in actual_cols for col in required_cols)

    if not has_required:
        print("\n⚠ 필수 컬럼이 부족합니다. 실제 데이터 구조 예시:")
        print(combined_data.head(5).to_string())
        print("\n💡 다음 단계:")
        print("   1. 실제 Excel 파일의 컬럼명 확인")
        print("   2. constants.py의 EXCEL_COLUMNS 매핑 수정")
        print("   3. data_loader.py에서 컬럼 변환 로직 추가")
    else:
        # 환자단위 지표 계산
        calculator = PatientMetricsCalculator()
        results = calculator.calculate_by_mode(combined_data)

        print("\n✓ 성능 지표 계산 완료!")
        print("\n" + "=" * 80)
        print("📊 분석 결과")
        print("=" * 80)

        # Assisted vs Unaided 결과 출력
        for mode in ['assisted', 'unaided']:
            if mode in results:
                print(f"\n[{mode.upper()}]")
                metrics = results[mode]['metrics']
                cm = results[mode]['confusion_matrix']

                print(f"  환자 수: {results[mode]['n_patients']}명")
                print(f"\n  Confusion Matrix:")
                print(f"    TP: {cm['TP']}, FP: {cm['FP']}")
                print(f"    FN: {cm['FN']}, TN: {cm['TN']}")
                print(f"\n  성능 지표:")
                print(f"    Sensitivity: {metrics['sensitivity']:.3f} ({metrics['sensitivity']*100:.1f}%)")
                print(f"    Specificity: {metrics['specificity']:.3f} ({metrics['specificity']*100:.1f}%)")
                print(f"    PPV:         {metrics['ppv']:.3f} ({metrics['ppv']*100:.1f}%)")
                print(f"    NPV:         {metrics['npv']:.3f} ({metrics['npv']*100:.1f}%)")

        # Delta 계산
        if 'assisted' in results and 'unaided' in results:
            delta = calculator.calculate_delta()
            print("\n" + "-" * 80)
            print("Δ (Assisted - Unaided)")
            print("-" * 80)
            for metric, value in delta.items():
                metric_name = metric.replace('delta_', '').upper()
                direction = "↑" if value > 0 else "↓" if value < 0 else "="
                print(f"  {metric_name}: {value:+.3f} ({value*100:+.1f}%) {direction}")

        # 비교 테이블 생성
        comparison_table = calculator.create_comparison_table()
        print("\n" + "=" * 80)
        print("📊 비교 테이블")
        print("=" * 80)
        print(comparison_table.to_string(index=False))

        # 결과 저장
        results_dir = Path(__file__).parent / "results" / "tables"
        results_dir.mkdir(parents=True, exist_ok=True)

        comparison_table.to_csv(results_dir / "comparison_table.csv", index=False)
        calculator.export_metrics(results_dir / "patient_metrics.json")

        print(f"\n✓ 결과 저장 완료:")
        print(f"  - {results_dir / 'comparison_table.csv'}")
        print(f"  - {results_dir / 'patient_metrics.json'}")

except Exception as e:
    print(f"\n✗ 분석 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
