## Project overview

This directory contains scripts to run the same collinear triatomic system (H, H, Ne on the x-axis) with Gaussian, CP2K, and Quantum ESPRESSO (QE), over a 71×71 grid of coordinates, and to parse outputs into spreadsheets.

### System and grid
- Atomic positions (Å):
  - `H  (0.0, 0.0, 0.0)`
  - `H  (n,   0.0, 0.0)`
  - `Ne (m,   0.0, 0.0)`
- Grid definition: `m = 0.5 + 0.05*i`, `n = -0.5 - 0.05*j`, with `i, j ∈ [0, 70]`. Each grid point is stored in a subdirectory named `Ne{m},H{n}`.

## Files

- Gaussian
  - `generate_gaussian_input.py`: generate `.gjf` inputs in all subfolders
  - `g09.sh`: batch run Gaussian (`g16` by default; adjust as needed)
  - `read.py` or `read_gaussian.py`: parse Gaussian outputs to Excel

- CP2K
  - `generate_cp2k_input.py`: generate `cp2k.inp` in all subfolders
  - `cp2k.sh`: batch run CP2K
  - `read_cp2k.py`: parse `cp2k.out` to Excel

- Quantum ESPRESSO
  - `generate_qe_input.py`: generate `pw.in` in all subfolders
  - `qe.sh`: batch run QE (`pw.x`)
  - `read_qe.py`: parse `pw.out` to Excel

## Requirements

- Python 3 (for generators and parsers)
- Disk space sufficient for 71×71 runs
- Gaussian (`g16`/`g09`), CP2K (`cp2k.psmp`), QE (`pw.x`) properly installed
- Pseudopotentials/atomic data available:
  - CP2K: `BASIS_MOLOPT`, `GTH_POTENTIALS` reachable by CP2K
  - QE: place UPF files under `./pseudo/`, matching names in `ATOMIC_SPECIES`

## Generate inputs

### Gaussian
```bash
python3 generate_gaussian_input.py
```

### CP2K
```bash
python3 generate_cp2k_input.py
```

### QE
```bash
python3 generate_qe_input.py
```

## Batch runs

### Gaussian
```bash
bash g09.sh
```

### CP2K
```bash
bash cp2k.sh /path/to/cp2k.psmp
# or, if cp2k.psmp is in PATH
bash cp2k.sh
```

### QE
```bash
bash qe.sh /path/to/pw.x
# or, if pw.x is in PATH
bash qe.sh
```

## Parse outputs to Excel

Each parser scans `Ne{m},H{n}` folders (m, n as defined above) and writes a spreadsheet with columns `x, y, z`, where `z` is total energy in Hartree (Ha). For Gaussian parsing, `read.py` is the original script; `read_gaussian.py` is a robust alternative.

- Gaussian
```bash
python3 read_gaussian.py
# outputs: gaussian_energy.xlsx, gaussian_errors.xlsx
```

- CP2K
```bash
python3 read_cp2k.py
# outputs: cp2k_energy.xlsx, cp2k_errors.xlsx
```

- QE
```bash
python3 read_qe.py
# outputs: qe_energy.xlsx, qe_errors.xlsx
```

Notes:
- CP2K energy is read from lines like `ENERGY| Total FORCE_EVAL ( QS ) energy (a.u.): ...`.
- QE energy is read from lines like `!    total energy = ... Ry` and converted to Hartree by `E_Ha = E_Ry × 0.5`.

## Consistency

- Charge/spin: Gaussian route uses `1 2` (charge = +1, multiplicity = 2). CP2K and QE templates are set accordingly.
- Functional and numerics: templates use B3LYP-like settings. For large scans or faster turnaround, consider switching to PBE and adjusting cutoffs.
- Box/periodicity: Large cubic box (~30 Å) and Γ-point sampling approximate non-periodic conditions.

## Troubleshooting

- Missing data files: ensure CP2K basis/potentials and QE pseudopotentials are available and paths match.
- SCF convergence: reduce mixing or loosen thresholds, preconverge with a GGA first, or increase max iterations.
- Throughput: use your scheduler (SLURM/PBS) or GNU Parallel to spread subfolders across nodes/cores; mind I/O quotas.


