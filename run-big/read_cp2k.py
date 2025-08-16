import os
import re
import pandas as pd


ENERGY_PATTERN = re.compile(
    r"ENERGY\|\s*Total FORCE_EVAL.*?energy \(a\.u\.\):\s*([-0-9\.Ee\+]+)")


def extract_energy_from_cp2k(output_path: str):
    try:
        with open(output_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None

    if re.search(r"ERROR", content, flags=re.IGNORECASE):
        return None

    matches = ENERGY_PATTERN.findall(content)
    if matches:
        return float(matches[-1])  # Hartree

    # 备选关键词（部分版本可能不同）
    alt_matches = re.findall(r"Total energy:\s*([-0-9\.Ee\+]+)\s*a\.u\.\.", content)
    if alt_matches:
        return float(alt_matches[-1])

    return None


def main():
    data_rows = []
    error_rows = []

    for i in range(71):
        for j in range(71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            out_path = os.path.join(f"Ne{m},H{n}", "cp2k.out")
            energy = extract_energy_from_cp2k(out_path)
            if energy is None:
                error_rows.append((m, n))
                print(f"Error: {out_path}")
            else:
                data_rows.append((m, -n, energy))
                print(f"From {out_path}: E(Ha)={energy}")

    if data_rows:
        df = pd.DataFrame(data_rows, columns=["x", "y", "z"])  # z 为能量（Hartree）
        df.to_excel("cp2k_energy.xlsx", index=False)

    if error_rows:
        dfe = pd.DataFrame(error_rows, columns=["x", "y"])  # 坐标对（失败）
        dfe.to_excel("cp2k_errors.xlsx", index=False)


if __name__ == "__main__":
    main()


