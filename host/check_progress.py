"""
Monitor progress of comprehensive test runs.
"""

import csv
from pathlib import Path
from datetime import datetime

def check_progress():
    results_file = Path("../results/comprehensive_results.csv")

    if not results_file.exists():
        print("No results file found yet. Tests may still be starting...")
        return

    # Read results
    with open(results_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) == 0:
        print("Results file is empty. Tests are starting...")
        return

    total_expected = 42 * 3  # 42 cases × 3 precisions
    completed = len(rows)
    success_count = sum(1 for r in rows if r.get('status') == 'success')
    failed_count = completed - success_count

    print("="*80)
    print(f"Test Progress Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"\nOverall Progress: {completed}/{total_expected} ({completed/total_expected*100:.1f}%)")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")

    if completed > 0:
        # Latest result
        latest = rows[-1]
        print(f"\nLatest Test:")
        print(f"  Case: {latest.get('case_id')} ({latest.get('category')})")
        print(f"  Precision: {latest.get('precision')}")
        print(f"  Status: {latest.get('status')}")
        if latest.get('status') == 'success':
            print(f"  RMSE: {latest.get('rmse', 'N/A')}")
            print(f"  Time: {latest.get('sim_time_sec', 'N/A')}s")

    # Estimate remaining time
    if success_count > 0:
        avg_time = sum(float(r.get('sim_time_sec', 0)) for r in rows if r.get('status') == 'success') / success_count
        remaining = total_expected - completed
        est_time = remaining * avg_time
        hours = int(est_time // 3600)
        minutes = int((est_time % 3600) // 60)
        print(f"\nEstimated time remaining: {hours}h {minutes}m")
        print(f"  (based on avg {avg_time:.1f}s per test)")

    # Success rate by precision
    print("\nSuccess Rate by Precision:")
    for prec in ['int8', 'fp16', 'fp32']:
        prec_rows = [r for r in rows if r.get('precision') == prec]
        if prec_rows:
            prec_success = sum(1 for r in prec_rows if r.get('status') == 'success')
            print(f"  {prec}: {prec_success}/{len(prec_rows)} ({prec_success/len(prec_rows)*100:.0f}%)")

    print("\n" + "="*80)

if __name__ == '__main__':
    check_progress()
