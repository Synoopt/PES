import os
import re
import numpy as np
import pandas as pd


def extract_energy_from_gaussian(output_path: str):
    try:
        with open(output_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None

    # 按原脚本风格：若包含 Error 则视为失败
    if re.search(r"Error", content, flags=re.IGNORECASE):
        return None

    # 与现有 read.py 保持一致：抓取最后一个 "HF=" 值（字符串切片方式不可控，这里用正则更稳健）
    # 说明：Gaussian 的 B3LYP 单点通常也会出现 HF= 记录；若你的版本/关键词不含此字段，可改为匹配 "SCF Done" 行。
    matches = re.findall(r"HF=\s*([-0-9\.Ee+]+)", content)
    if matches:
        return float(matches[-1])

    # 备选：匹配 SCF Done 行
    matches = re.findall(r"SCF Done:\s+E\([^)]*\)\s*=\s*([-0-9\.Ee+]+)", content)
    if matches:
        return float(matches[-1])

    return None


def main():
    data_rows = []
    error_rows = []

    for i in range(71):
        for j in range(71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            out_path = os.path.join(f"Ne{m},H{n}", f"Ne{m},H{n}.out")
            energy = extract_energy_from_gaussian(out_path)
            if energy is None:
                error_rows.append((m, n))
                print(f"Error: {out_path}")
            else:
                # 保持与原脚本相同：y 取 -n（见 read.py 第 49 行）
                data_rows.append((m, -n, energy))
                print(f"From {out_path}: E(Ha)={energy}")

    if data_rows:
        df = pd.DataFrame(data_rows, columns=["x", "y", "z"])  # z 为能量（Hartree）
        df.to_excel("gaussian_energy.xlsx", index=False)

    if error_rows:
        dfe = pd.DataFrame(error_rows, columns=["x", "y"])  # 坐标对（失败）
        dfe.to_excel("gaussian_errors.xlsx", index=False)


if __name__ == "__main__":
    main()


