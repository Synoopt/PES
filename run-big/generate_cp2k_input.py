import os


HEADER_TEMPLATE = """
&GLOBAL
  PROJECT {project}
  RUN_TYPE ENERGY_FORCE
&END GLOBAL

&FORCE_EVAL
  METHOD QUICKSTEP
  &DFT
    CHARGE 1
    UKS TRUE
    MULTIPLICITY 2

    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS

    &MGRID
      CUTOFF 600
      REL_CUTOFF 60
    &END MGRID

    &SCF
      SCF_GUESS ATOMIC
      EPS_SCF 1.0E-7
      MAX_SCF 200
    &END SCF

    &XC
      &XC_FUNCTIONAL B3LYP
      &END XC_FUNCTIONAL
      &HF
        FRACTION 0.20
        &SCREENING
          EPS_SCHWARZ 1.0E-6
        &END SCREENING
      &END HF
    &END XC
  &END DFT

  &SUBSYS
    &CELL
      ABC 30.0 30.0 30.0
      PERIODIC NONE
    &END CELL
    &COORD
      H   0.000000  0.000000  0.000000
      H   {h2x: .6f}  0.000000  0.000000
      Ne  {nex: .6f}  0.000000  0.000000
    &END COORD

    &KIND H
      BASIS_SET TZV2P-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
    &KIND Ne
      BASIS_SET TZV2P-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
"""


def write_cp2k_input(directory: str, m: float, n: float) -> None:
    project = f"Ne{m},H{n}"
    content = HEADER_TEMPLATE.format(project=project, nex=m, h2x=n)
    inp_path = os.path.join(directory, "cp2k.inp")
    with open(inp_path, "w") as f:
        f.write(content)


def main() -> None:
    for i in range(0, 71):
        for j in range(0, 71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            dirname = f"Ne{m},H{n}"
            os.makedirs(dirname, exist_ok=True)
            write_cp2k_input(dirname, m, n)

    print("CP2K 输入已生成（文件名：cp2k.inp）。请确保以下文件可用并在 CP2K 运行环境可见：")
    print("- BASIS_MOLOPT（通常随 CP2K 发布，如 data/BASIS_MOLOPT）")
    print("- GTH_POTENTIALS（通常随 CP2K 发布，如 data/GTH_POTENTIALS）")


if __name__ == "__main__":
    main()


