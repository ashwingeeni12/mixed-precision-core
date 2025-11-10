import os, csv, subprocess, pathlib, time
from itertools import product

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = ROOT/"host"
MEM  = ROOT/"mem"
RES  = ROOT/"results"
RES.mkdir(exist_ok=True)

def run(cmd, env=None):
    print("$", " ".join(cmd))
    r = subprocess.run(cmd, env=env, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(cmd)}")

def read_csv(path):
    import numpy as np
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append([float(x) for x in line.strip().split(',')])
    return np.array(rows, dtype=float)

PRECODES = {"int8":0, "fp16":1, "fp32":2}

def main():
    sizes = [(4,4,4),(8,8,8)]  # extend as desired
    precs = ["int8","fp16","fp32"]

    with open(RES/"metrics.csv","w", newline='') as fc:
        w = csv.writer(fc)
        w.writerow(["timestamp","prec","M","K","N","MAE","RMSE","MAX_ABS","REL_MAE","REL_RMSE"])

        for (M,K,N), p in product(sizes, precs):
            # 1) generate inputs + reference
            run(["python3", str(HOST/"gen_mems.py"), "--M", str(M), "--K", str(K), "--N", str(N), "--prec", p])
            # 2) simulate one run
            env = os.environ.copy()
            env["PREC_SEL"] = str(PRECODES[p])
            env["M"], env["K"], env["N"] = str(M), str(K), str(N)
            run(["vivado","-mode","batch","-source","scripts/run_sim.tcl"], env=env)
            # 3) parse output (convert raw to floats)
            run(["python3", str(HOST/"parse_out_to_csv.py"), "--M", str(M), "--N", str(N), "--prec", p])
            # 4) compute metrics vs reference
            import numpy as np, time
            C_ref = read_csv(MEM/"C_ref.csv")
            C_out = read_csv(MEM/"C_out.csv")
            diff  = C_out - C_ref
            mae   = float(np.mean(np.abs(diff)))
            rmse  = float(np.sqrt(np.mean(diff**2)))
            maxa  = float(np.max(np.abs(diff)))
            denom = np.maximum(np.abs(C_ref), 1e-6)
            rel_mae = float(np.mean(np.abs(diff)/denom))
            rel_rmse = float(np.sqrt(np.mean((diff/denom)**2)))
            w.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), p, M, K, N, mae, rmse, maxa, rel_mae, rel_rmse])
            fc.flush()
            print(f"[OK] {p} {M}x{K}x{N} MAE={mae:.4g} RMSE={rmse:.4g} MaxAbs={maxa:.4g}")

if __name__=='__main__':
    main()
