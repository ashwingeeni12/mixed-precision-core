"""
Simple script to test a single simulation
"""
import subprocess
import os
from pathlib import Path

# Setup
ROOT = Path(__file__).parent
VIVADO_BIN = Path("D:/ashwin_shit/2025.1/Vivado/bin")

# Set environment
env = os.environ.copy()
env["PREC_SEL"] = "0"
env["M"] = "8"
env["K"] = "8"
env["N"] = "8"

print("=" * 80)
print("Testing single simulation workflow")
print(f"PREC_SEL={env['PREC_SEL']} M={env['M']} K={env['K']} N={env['N']}")
print("=" * 80)

os.chdir(ROOT)

# Create sim_defines.vh
print("\n[0/3] Creating sim_defines.vh...")
with open("src/sim_defines.vh", "w") as f:
    f.write("// Auto-generated defines\n")
    f.write(f"`define PREC_SEL {env['PREC_SEL']}\n")
    f.write(f"`define M {env['M']}\n")
    f.write(f"`define K {env['K']}\n")
    f.write(f"`define N {env['N']}\n")

# Step 1: Compile
print("\n[1/3] Compiling...")
result = subprocess.run([
    str(VIVADO_BIN / "xvlog.bat"),
    "-sv", "-i", "src",
    "--work", "xil_defaultlib",
    "--prj", "compile.prj"
], env=env)

if result.returncode != 0:
    print(f"ERROR: Compilation failed with code {result.returncode}")
    exit(1)

print("Compilation successful!")

# Step 2: Elaborate (without glbl)
print("\n[2/3] Elaborating...")
result = subprocess.run([
    str(VIVADO_BIN / "xelab.bat"),
    "-debug", "typical",
    "-relax",
    "--snapshot", "tb_top_gemm_snap",
    "xil_defaultlib.tb_top_gemm"
], env=env)

if result.returncode != 0:
    print(f"ERROR: Elaboration failed with code {result.returncode}")
    exit(1)

print("Elaboration successful!")

# Step 3: Simulate
print("\n[3/3] Running simulation...")
result = subprocess.run([
    str(VIVADO_BIN / "xsim.bat"),
    "tb_top_gemm_snap",
    "--tclbatch", "scripts/run_xsim.tcl",
    "--log", "xsim.log"
], env=env)

if result.returncode != 0:
    print(f"ERROR: Simulation failed with code {result.returncode}")
    exit(1)

print("Simulation successful!")

# Check output
if (ROOT / "mem" / "C_out.mem").exists():
    print("\n" + "=" * 80)
    print("SUCCESS! Output file created: mem/C_out.mem")
    print("=" * 80)
else:
    print("\nWARNING: Output file not found")
    exit(1)
