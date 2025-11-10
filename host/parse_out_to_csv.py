
import argparse, struct, csv, numpy as np

def f16_to_float(u16: int) -> float:
    return float(np.float16(np.uint16(u16)))

def f32_to_float(u32: int) -> float:
    import struct
    return struct.unpack('<f', struct.pack('<I', u32 & 0xffffffff))[0]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--M', type=int, required=True)
    p.add_argument('--N', type=int, required=True)
    p.add_argument('--prec', choices=['int8','fp16','fp32'], required=True)
    args = p.parse_args()

    vals = []
    undefined_count = 0
    with open('../mem/C_out.mem','r') as f:
        for line_num, line in enumerate(f, 1):
            t = line.strip()
            if not t: continue
            # Handle undefined values (xxxxxxxx) by treating as 0
            if 'x' in t.lower():
                vals.append(0)
                undefined_count += 1
                print(f"Warning: Line {line_num} has undefined value '{t}', using 0")
            else:
                vals.append(int(t,16))

    if undefined_count > 0:
        print(f"Warning: Found {undefined_count} undefined value(s) in output")

    M,N = args.M, args.N
    assert len(vals) >= M*N, "C_out.mem smaller than expected"

    with open('../mem/C_out.csv','w', newline='') as fc:
        w = csv.writer(fc)
        for i in range(M):
            row = []
            for j in range(N):
                u = vals[i*N + j]
                if args.prec=='int8':
                    if u & 0x80000000: u = -((~u + 1) & 0xffffffff)
                    row.append(int(u))
                elif args.prec=='fp16':
                    row.append(f16_to_float(u & 0xffff))
                else:
                    row.append(f32_to_float(u))
            w.writerow(row)

    print("Wrote mem/C_out.csv")

if __name__=='__main__':
    main()
