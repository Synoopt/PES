## 项目说明

本目录提供将同一三原子体系（H、H、Ne，位于同一直线上）在三种量化软件中进行批量单点能/力计算的脚本：Gaussian、CP2K、Quantum ESPRESSO（QE）。三套脚本共享同一坐标网格与目录命名（`Ne{m},H{n}`）。

### 体系与网格
- 原子坐标（Å）：
  - `H  (0.0, 0.0, 0.0)`
  - `H  (n,   0.0, 0.0)`
  - `Ne (m,   0.0, 0.0)`
- 网格：`m = 0.5 + 0.05*i`，`n = -0.5 - 0.05*j`，`i, j ∈ [0, 70]`，共 71×71 个子目录。

## 文件清单

- Gaussian（已存在）
  - `generate_gaussian_input.py`：批量生成 `.gjf`
  - `g09.sh`：批量运行 `g16`（或改为 `g09`）
  - `read.py`：从 Gaussian 输出中提取能量（HF）等，写入 `input_force.xlsx`
  - `read_gaussian.py`：解析 Gaussian `*.out`，输出 `gaussian_energy.xlsx`、`gaussian_errors.xlsx`

- CP2K（新增）
  - `generate_cp2k_input.py`：批量生成 `cp2k.inp`
  - `cp2k.sh`：批量调用 `cp2k.psmp`（或你环境中的可执行）
  - `read_cp2k.py`：解析 `cp2k.out`，输出 `cp2k_energy.xlsx`、`cp2k_errors.xlsx`

- Quantum ESPRESSO（新增）
  - `generate_qe_input.py`：批量生成 `pw.in`
  - `qe.sh`：批量调用 `pw.x`
  - `read_qe.py`：解析 `pw.out`，输出 `qe_energy.xlsx`、`qe_errors.xlsx`

## 环境准备

### 共同要求
- Python 3（用于生成输入）
- 足够磁盘空间（71×71 网格会生成大量子目录与输出文件）

### Gaussian
- 已安装 `g16` 或 `g09`，并设置 `GAUSS_SCRDIR`

### CP2K
- 已安装 CP2K（建议并行版 `cp2k.psmp`）
- 数据文件可见：
  - `BASIS_MOLOPT`（常见路径示例：`$CP2K_DATA/BASIS_MOLOPT`）
  - `GTH_POTENTIALS`（常见路径示例：`$CP2K_DATA/GTH_POTENTIALS`）

### Quantum ESPRESSO
- 已安装 QE（`pw.x`）
- 在本目录下准备 `pseudo/` 赝势文件（文件名要与 `pw.in` 中一致）：
  - `H.pbe-rrkjus.UPF`
  - `Ne.pbe-n-rrkjus_psl.1.0.0.UPF`

## 生成输入

### Gaussian
```bash
python3 generate_gaussian_input.py
```

### CP2K
```bash
python3 generate_cp2k_input.py
```
生成的每个子目录包含 `cp2k.inp`。

### Quantum ESPRESSO
```bash
python3 generate_qe_input.py
```
生成的每个子目录包含 `pw.in`。

## 批量运行

### Gaussian
```bash
bash g09.sh
```
脚本会遍历 `*/*.gjf`，输出写入对应的 `.out`。

### CP2K
```bash
# 指定可执行（可选）
bash cp2k.sh /path/to/cp2k.psmp
# 或使用 PATH 中的 cp2k.psmp
bash cp2k.sh
```
输出写入各子目录 `cp2k.out`。

并行提示：如果需要使用 `mpirun`，可编辑脚本将可执行替换为 `mpirun -np N cp2k.psmp`，或在调度系统作业脚本中显式使用 `mpirun`/`srun`。

### Quantum ESPRESSO
```bash
# 指定可执行（可选）
bash qe.sh /path/to/pw.x
# 或使用 PATH 中的 pw.x
bash qe.sh
```
输出写入各子目录 `pw.out`。

并行提示：同上，若需 `mpirun -np N pw.x`，建议在作业脚本中直接写完整命令，或修改 `qe.sh`，避免在脚本里传入带空格的命令字符串。

## 结果提取与比对

- Gaussian（两种脚本任选其一）：
  - 原脚本（与历史表格兼容）：
    ```bash
    python3 read.py
    ```
    生成 `input_force.xlsx`（列为 x, y, z，其中 z 为 HF 能量）。
  - 新增解析脚本（更稳健的正则匹配）：
    ```bash
    python3 read_gaussian.py
    ```
    生成 `gaussian_energy.xlsx`、失败清单 `gaussian_errors.xlsx`。

- CP2K：
  ```bash
  python3 read_cp2k.py
  ```
  生成 `cp2k_energy.xlsx`、`cp2k_errors.xlsx`。

- Quantum ESPRESSO：
  ```bash
  python3 read_qe.py
  ```
  生成 `qe_energy.xlsx`、`qe_errors.xlsx`（能量由 Ry 转换为 Ha，系数 0.5）。

如需将三套能量汇总到一个 Excel 进行对比，可告知需要的表头格式，我可以补充合并脚本。

## 重要参数与一致性说明

- 电荷/自旋：
  - Gaussian 输入为 `1 2`（电荷=+1，自旋多重度=2）。
  - CP2K：`CHARGE 1`、`UKS TRUE`、`MULTIPLICITY 2`。
  - QE：`tot_charge = 1`、`nspin = 2`，对 `H` 设 `starting_magnetization(1) = 1.0`（按 `ATOMIC_SPECIES` 顺序）。

- 泛函/数值参数：
  - Gaussian：`# sp b3lyp/6-311g** Force nosymm scf=(qc)`。
  - CP2K：模板使用 `B3LYP`（含 `&HF` 分数），基组为 `TZV2P-MOLOPT-GTH`、赝势 `GTH-PBE`，`CUTOFF 600`、`REL_CUTOFF 60`（可按需调高/调低）。
  - QE：模板写了 `input_dft='B3LYP'`，`ecutwfc=80`、`ecutrho=640`。混合泛函在平面波框架开销较大，若为快速扫描或与赝势更匹配，可改为 `PBE` 并相应调整 `ecutwfc/ecutrho`。

- 盒子/周期性：
  - CP2K：`ABC 30 30 30`，`PERIODIC NONE`。
  - QE：`ibrav=0` + 30 Å 立方盒 + Γ 点近似非周期。

如需与 Gaussian 严格可比，请统一：泛函、基组/赝势、SCF 收敛阈值及数值参数，并确保足够大的盒子以避免镜像相互作用。

## 常见问题（FAQ）

- 找不到赝势/基组文件：
  - CP2K：检查 `BASIS_SET_FILE_NAME`、`POTENTIAL_FILE_NAME` 路径；确保环境变量或绝对路径正确。
  - QE：确保赝势位于 `pseudo/` 且文件名与 `ATOMIC_SPECIES` 一致。

- SCF 不收敛：
  - 降低 `mixing_beta`（QE）、提高 `MAX_SCF`/`EPS_SCF`（CP2K），或给出更好初猜；尝试改成 GGA 先收敛再切回混合泛函。

- 批量并行：
  - 若要并行跑多个子目录，可结合集群调度系统（SLURM/PBS）或 `GNU parallel`。注意 I/O 与磁盘配额。

## 目录结构示例

```text
run-big/
  generate_gaussian_input.py
  g09.sh
  read.py
  read_gaussian.py
  generate_cp2k_input.py
  cp2k.sh
  read_cp2k.py
  generate_qe_input.py
  qe.sh
  read_qe.py
  pseudo/                # QE 赝势（需自备）
  Ne0.5,H-0.5/
    Ne0.5,H-0.5.gjf
    cp2k.inp
    pw.in
    ...
```

## 备注

- 上述脚本默认会生成 71×71 个子目录，体量较大；如仅测试，请先临时缩小循环范围。
- 如果你希望我提供三套结果的合并与对比脚本，请告知输出格式需求。


