"""
Generate all 42 matrix test cases with controlled condition numbers.
Saves each test case in a separate directory for manual simulation.
"""

import subprocess
import pathlib
import json
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = ROOT / "host"
TEST_CASES_DIR = ROOT / "test_cases"
TEST_CASES_DIR.mkdir(exist_ok=True)

def generate_all_test_cases():
    """Generate all 42 test matrix pairs."""

    M, K, N = 8, 8, 8
    precs = ["int8", "fp16", "fp32"]
    num_cases = 42

    print("="*80)
    print(f"Generating {num_cases} test matrix pairs")
    print("="*80)

    all_metadata = []

    for case_id in range(num_cases):
        for prec in precs:
            print(f"\nGenerating Case {case_id}, Precision {prec}...")

            # Create directory for this test
            test_dir = TEST_CASES_DIR / f"case_{case_id:02d}_{prec}"
            test_dir.mkdir(exist_ok=True)

            # Generate matrices
            cmd = [
                "python", str(HOST / "gen_cond_mems.py"),
                "--M", str(M), "--K", str(K), "--N", str(N),
                "--prec", prec,
                "--case-id", str(case_id),
                "--output-dir", str(test_dir)
            ]

            result = subprocess.run(cmd, cwd=HOST, capture_output=True, text=True)

            if result.returncode == 0:
                # Load and save metadata
                metadata_path = test_dir / "test_metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    all_metadata.append(metadata)
                    print(f"  [OK] Generated successfully")
                    print(f"    Category: {metadata['category']}")
                    print(f"    Cond(A): {metadata['actual_cond_A']:.2f}, Cond(B): {metadata['actual_cond_B']:.2f}")
                else:
                    print(f"  [ERROR] Metadata file not found")
            else:
                print(f"  [ERROR] Generation failed:")
                print(f"    {result.stderr}")

    # Save consolidated metadata
    with open(TEST_CASES_DIR / "all_test_metadata.json", 'w') as f:
        json.dump(all_metadata, f, indent=2)

    print("\n" + "="*80)
    print(f"Generated {len(all_metadata)} test cases")
    print(f"Saved to: {TEST_CASES_DIR}")
    print("="*80)

    # Create summary
    categories = {}
    for meta in all_metadata:
        cat = meta['category']
        prec = meta['precision']
        key = f"{cat}_{prec}"
        categories[key] = categories.get(key, 0) + 1

    print("\nSummary by Category and Precision:")
    for prec in ["int8", "fp16", "fp32"]:
        print(f"\n{prec.upper()}:")
        for cat in ["low", "medium", "high"]:
            count = categories.get(f"{cat}_{prec}", 0)
            print(f"  {cat.capitalize()}: {count} cases")

if __name__ == '__main__':
    generate_all_test_cases()
