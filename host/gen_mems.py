
import argparse, struct, random, numpy as np, csv

def f16_from_float(x: float) -> int:
    return int(np.float16(x).view('H'))

def f32_from_float(x: float) -> int:
    return struct.unpack('<I', struct.pack('<f', x))[0]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--M', type=int, required=True)
    p.add_argument('--K', type=int, required=True)
    p.add_argument('--N', type=int, required=True)
    p.add_argument('--prec', choices=['int8','fp16','fp32'], required=True)
    p.add_argument('--range', type=float, default=3.0)
    p.add_argument('--seed', type=int, default=1)
    args = p.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    M,K,N = args.M, args.K, args.N

    if args.prec=='int8':
        A = np.random.randint(-5,6,size=(M,K),dtype=np.int8)
        B = np.random.randint(-5,6,size=(K,N),dtype=np.int8)
    else:
        A = (np.random.rand(M,K)*2-1)*args.range
        B = (np.random.rand(K,N)*2-1)*args.range

    with open('../mem/A.mem','w') as fa:
        for i in range(M):
            for k in range(K):
                if args.prec=='int8':
                    val = int(A[i,k]) & 0xff
                elif args.prec=='fp16':
                    val = f16_from_float(float(A[i,k]))
                else:
                    val = f32_from_float(float(A[i,k]))
                fa.write(f"{val:08x}\n")

    with open('../mem/B.mem','w') as fb:
        for k in range(K):
            for j in range(N):
                if args.prec=='int8':
                    val = int(B[k,j]) & 0xff
                elif args.prec=='fp16':
                    val = f16_from_float(float(B[k,j]))
                else:
                    val = f32_from_float(float(B[k,j]))
                fb.write(f"{val:08x}\n")

    # ground truth (float32)
    C = A.astype(np.float64) @ B.astype(np.float64)
    with open('../mem/C_ref.csv','w', newline='') as fc:
        w = csv.writer(fc)
        for i in range(M):
            w.writerow([float(C[i,j]) for j in range(N)])

    print("Wrote mem/A.mem, mem/B.mem, mem/C_ref.csv")

if __name__=='__main__':
    main()
