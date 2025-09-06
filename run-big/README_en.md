# PES Project - Potential Energy Surface Calculation Toolkit

## Overview

The PES (Potential Energy Surface) project is a comprehensive toolkit for calculating potential energy surfaces of three-atom systems, supporting three quantum chemistry software packages: Gaussian, CP2K, and Quantum ESPRESSO. This project provides complete functionality for input file generation, calculation execution, and result extraction.

## Key Features

- **Multi-software Support**: Gaussian, CP2K, Quantum ESPRESSO
- **Unified Configuration**: Centralized management of atom types, charge, and spin multiplicity
- **Force Calculation**: All software packages support energy and force calculations
- **Batch Processing**: Automatic generation of 71×71 grid calculation points
- **Result Extraction**: Automatic extraction of energy and force information, generating CSV format output
- **Ionic State Configuration**: Support for custom charge and spin multiplicity

## Project Structure

```
run-big/
├── README_zh.md                 # Chinese documentation
├── README_en.md                 # English documentation
├── atom_config.py               # Unified configuration file
├── generate_gaussian_input.py   # Gaussian input file generator
├── generate_cp2k_input.py       # CP2K input file generator
├── generate_qe_input.py         # QE input file generator
├── read_gaussian.py             # Gaussian result reader
├── read_cp2k.py                # CP2K result reader
├── read_qe.py                  # QE result reader
├── config_reader.py             # Configuration reading module
├── g09.sh                      # Gaussian calculation script
├── cp2k.sh                     # CP2K calculation script
├── qe.sh                       # QE calculation script
└── Other support files...
```

## Configuration

### Atom Configuration

Configure atom types in `atom_config.py`:

```python
# Atom configuration
ATOM1 = 'H'    # First atom type
ATOM2 = 'H'    # Second atom type  
ATOM3 = 'Ne'   # Third atom type

# Charge and multiplicity configuration
CHARGE = 1      # Total charge (0 = neutral, 1 = +1, -1 = -1, etc.)
MULTIPLICITY = 2  # Spin multiplicity (1 = singlet, 2 = doublet, 3 = triplet, etc.)
```

### Preset Configuration Examples

```python
# Organic molecular system
# ATOM1 = 'C'  # Carbon atom
# ATOM2 = 'H'  # Hydrogen atom
# ATOM3 = 'O'  # Oxygen atom
# CHARGE = 0   # Neutral molecule
# MULTIPLICITY = 1  # Singlet state

# Alkali metal system
# ATOM1 = 'Li'  # Lithium atom
# ATOM2 = 'Na'  # Sodium atom
# ATOM3 = 'K'   # Potassium atom
# CHARGE = 1    # +1 charge
# MULTIPLICITY = 2  # Doublet state

# Halogen system
# ATOM1 = 'F'   # Fluorine atom
# ATOM2 = 'Cl'  # Chlorine atom
# ATOM3 = 'Br'  # Bromine atom
# CHARGE = -1   # -1 charge
# MULTIPLICITY = 2  # Doublet state
```

##  Output Format

### Unified CSV Format

All three software packages now output the same CSV format:

```csv
x,y,z1,z2,z3,z4
0.5,-0.5,-76.123456,0.000000,-0.123456,0.234567
0.55,-0.55,-76.123789,0.000000,-0.123789,0.234890
...
```

**Column Description:**
- `x`: First atom coordinate
- `y`: Second atom coordinate  
- `z1`: Total energy (Hartree)
- `z2`: First atom X-direction force (Hartrees/Bohr)
- `z3`: Second atom X-direction force (Hartrees/Bohr)
- `z4`: Third atom X-direction force (Hartrees/Bohr)

##  Usage Instructions

### 1. Generate Input Files

```bash
# Generate Gaussian input
python generate_gaussian_input.py

# Generate CP2K input  
python generate_cp2k_input.py

# Generate QE input
python generate_qe_input.py
```

### 2. Run Calculations

```bash
# Gaussian
cd H_H_Ne_gaussian_calculations
bash ../g09.sh

# CP2K
cd H_H_Ne_cp2k_calculations  
bash ../cp2k.sh

# QE
cd H_H_Ne_qe_calculations
bash ../qe.sh
```

### 3. Extract Results

```bash
# Extract Gaussian results
python ../read_gaussian.py

# Extract CP2K results
python ../read_cp2k.py

# Extract QE results
python ../read_qe.py
```

## ⚡ Force Calculation Features

### Gaussian
- Default force output, no additional configuration needed
- Search pattern: "Center Atomic Forces (Hartrees/Bohr)"

### CP2K
- Add force output section in input file:
```fortran
&PRINT
  &FORCES
    &EACH
      GEO_OPT 1
      MD 1
    &END EACH
  &END FORCES
&END PRINT
```

### QE
- Already includes force calculation setting: `tprnfor = .true.`
- Search pattern: "Forces acting on atoms (Ry/au):"

##  Data Statistics

Each read script displays:

```
   Data contains energy and force information
   Data statistics:
   Total rows: 5041
   Total columns: 6
   Force information completeness: 5041/5041 (100.0%)
```

## Important Notes

### 1. Physical Reasonableness
- Ensure charge and spin multiplicity match atom types
- Some combinations may be physically unreasonable

### 2. Calculation Stability
- High spin multiplicity may increase calculation difficulty
- Some charge states may require special handling

### 3. Basis Sets and Pseudopotentials
- After modifying atom types, ensure corresponding basis set/pseudopotential files exist
- Some atom combinations may require calculation parameter adjustments

## Troubleshooting

### Common Issues

1. **Missing Force Information**
   - Check if input files contain force calculation settings
   - Confirm calculations completed successfully
   - Review error messages in output files

2. **Format Mismatch**
   - Ensure latest version of read scripts are used
   - Check if output file format matches expectations

3. **Calculation Failure**
   - Check input parameter settings
   - Review software error logs
   - Verify atom types and basis set settings

### Debugging Tips

1. **Manual Output File Inspection**
   ```bash
   # View Gaussian output
   head -50 H_H_Ne_gaussian_calculations/Ne0.5,H-0.5/Ne0.5,H-0.5.out
   
   # View CP2K output
   head -50 H_H_Ne_cp2k_calculations/Ne0.5,H-0.5/cp2k.out
   
   # View QE output
   head -50 H_H_Ne_qe_calculations/Ne0.5,H-0.5/pw.out
   ```

2. **Test Single File**
   ```python
   # Test force extraction from single file
   from read_gaussian import extract_energy_and_forces_from_gaussian
   energy, f1, f2, f3 = extract_energy_and_forces_from_gaussian("path/to/output.out")
   print(f"Energy: {energy}, Forces: {f1}, {f2}, {f3}")
   ```

## Feature Comparison

| Feature | Gaussian | CP2K | QE |
|---------|----------|------|----|
| Energy Calculation | ✅ | ✅ | ✅ |
| Force Calculation | ✅ | ✅ | ✅ |
| CSV Output | ✅ | ✅ | ✅ |
| Unified Format | ✅ | ✅ | ✅ |

## References

- [Gaussian Manual - Charge and Multiplicity](https://gaussian.com/charge/)
- [CP2K Manual - DFT Settings](https://www.cp2k.org/)
- [Quantum ESPRESSO Manual - System Settings](https://www.quantum-espresso.org/)

## Summary

The PES project now provides:

**Unified Input Configuration**: All software packages support ionic state and spin multiplicity configuration  
**Force Calculation Enabled**: CP2K and QE now calculate and output force information  
**Unified Output Format**: All software packages generate CSV files in identical format  
**Complete Data Extraction**: Includes coordinates, energy, and X-direction forces for three atoms  

You can now use any software package to obtain completely consistent result formats!

## Getting Help

If you encounter issues, please:
1. Check configuration file syntax
2. Verify physical parameter reasonableness
3. Review software error logs
4. Contact technical support or consult relevant documentation


