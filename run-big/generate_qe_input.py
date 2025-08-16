import os


PW_TEMPLATE = """
&control
  calculation = 'scf'
  prefix = '{prefix}'
  pseudo_dir = './pseudo'
  outdir = './tmp'
  tprnfor = .true.
  tstress = .true.
/
&system
  ibrav = 0
  nat = 3
  ntyp = 2
  ecutwfc = 80
  ecutrho = 640
  input_dft = 'B3LYP'
  london = .false.
  nspin = 2
  starting_magnetization(1) = 1.0
  tot_charge = 1
/
&electrons
  conv_thr = 1.0d-8
  mixing_beta = 0.3
  electron_maxstep = 200
/
ATOMIC_SPECIES
  H  1.00794  H.pbe-rrkjus.UPF
  Ne 20.1797  Ne.pbe-n-rrkjus_psl.1.0.0.UPF

CELL_PARAMETERS angstrom
  30.0 0.0 0.0
  0.0 30.0 0.0
  0.0 0.0 30.0

ATOMIC_POSITIONS angstrom
  H  0.000000  0.000000  0.000000
  H  {h2x: .6f}  0.000000  0.000000
  Ne {nex: .6f}  0.000000  0.000000

K_POINTS gamma
"""


def write_qe_input(directory: str, m: float, n: float) -> None:
    prefix = f"Ne{m},H{n}"
    content = PW_TEMPLATE.format(prefix=prefix, nex=m, h2x=n)
    inp_path = os.path.join(directory, "pw.in")
    with open(inp_path, "w") as f:
        f.write(content)


def main() -> None:
    for i in range(0, 71):
        for j in range(0, 71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            dirname = f"Ne{m},H{n}"
            os.makedirs(dirname, exist_ok=True)
            write_qe_input(dirname, m, n)

    print("QE 输入已生成（文件名：pw.in）。请将赝势放在 ./pseudo 目录，并创建 ./tmp 供运行使用。")


if __name__ == "__main__":
    main()


