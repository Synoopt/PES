import os
import re
import pandas as pd


# QE 标准 SCF 输出能量行
RY_ENERGY_PATTERN = re.compile(r"!\s+total energy\s*=\s*([-0-9\.Ee\+]+)\s+Ry")


def extract_energy_from_qe(output_path: str):
    try:
        with open(output_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None

    if re.search(r"error|convergence NOT achieved", content, flags=re.IGNORECASE):
        return None

    matches = RY_ENERGY_PATTERN.findall(content)
    if matches:
        e_ry = float(matches[-1])
        e_ha = e_ry * 0.5  # 1 Ha = 2 Ry
        return e_ha

    # 备选：有些模块只输出 "total energy = ... Ry"（无 !）
    alt = re.findall(r"total energy\s*=\s*([-0-9\.Ee\+]+)\s+Ry", content)
    if alt:
        e_ry = float(alt[-1])
        return e_ry * 0.5

    return None


def main():
    data_rows = []
    error_rows = []

    for i in range(71):
        for j in range(71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            out_path = os.path.join(f"Ne{m},H{n}", "pw.out")
            energy = extract_energy_from_qe(out_path)
            if energy is None:
                error_rows.append((m, n))
                print(f"Error: {out_path}")
            else:
                data_rows.append((m, -n, energy))
                print(f"From {out_path}: E(Ha)={energy}")

    if data_rows:
        df = pd.DataFrame(data_rows, columns=["x", "y", "z"])  # z 为能量（Hartree）
        df.to_excel("qe_energy.xlsx", index=False)

    if error_rows:
        dfe = pd.DataFrame(error_rows, columns=["x", "y"])  # 坐标对（失败）
        dfe.to_excel("qe_errors.xlsx", index=False)


if __name__ == "__main__":
    main()


