import os

# Import configuration from unified config file
try:
    from atom_config import ATOM1, ATOM2, ATOM3, CHARGE, MULTIPLICITY
    print(f"✅ Loaded configuration from atom_config.py: {ATOM1}-{ATOM2}-{ATOM3}, Charge={CHARGE}, Multiplicity={MULTIPLICITY}")
except ImportError:
    # Fallback configuration if atom_config.py is not available
    print("⚠️ atom_config.py not found, using default configuration")
    ATOM1 = 'H'    # First atom type
    ATOM2 = 'H'    # Second atom type  
    ATOM3 = 'Ne'   # Third atom type
    CHARGE = 1      # Total charge (0 = neutral, 1 = +1, -1 = -1, etc.)
    MULTIPLICITY = 2  # Spin multiplicity (1 = singlet, 2 = doublet, 3 = triplet, etc.)

# Create main folder name
MAIN_FOLDER = f"{ATOM1}_{ATOM2}_{ATOM3}_qe_calculations"

# Atomic mass configuration (need to adjust based on actual atom types)
ATOMIC_MASSES = {
    'H': 1.00794,
    'He': 4.002602,
    'Li': 6.94,
    'Be': 9.0121831,
    'B': 10.81,
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'F': 18.998403163,
    'Ne': 20.1797,
    'Na': 22.98976928,
    'Mg': 24.305,
    'Al': 26.9815385,
    'Si': 28.085,
    'P': 30.973761998,
    'S': 32.06,
    'Cl': 35.45,
    'Ar': 39.948,
    'K': 39.0983,
    'Ca': 40.078
}

# Pseudopotential filename configuration (need to adjust based on actual atom types)
PSEUDO_FILES = {
    'H': 'H.pbe-rrkjus.UPF',
    'He': 'He.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Li': 'Li.pbe-s-rrkjus_psl.1.0.0.UPF',
    'Be': 'Be.pbe-n-rrkjus_psl.1.0.0.UPF',
    'B': 'B.pbe-n-rrkjus_psl.1.0.0.UPF',
    'C': 'C.pbe-n-rrkjus_psl.1.0.0.UPF',
    'N': 'N.pbe-n-rrkjus_psl.1.0.0.UPF',
    'O': 'O.pbe-n-rrkjus_psl.1.0.0.UPF',
    'F': 'F.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Ne': 'Ne.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Na': 'Na.pbe-spn-rrkjus_psl.1.0.0.UPF',
    'Mg': 'Mg.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Al': 'Al.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Si': 'Si.pbe-n-rrkjus_psl.1.0.0.UPF',
    'P': 'P.pbe-n-rrkjus_psl.1.0.0.UPF',
    'S': 'S.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Cl': 'Cl.pbe-n-rrkjus_psl.1.0.0.UPF',
    'Ar': 'Ar.pbe-n-rrkjus_psl.1.0.0.UPF',
    'K': 'K.pbe-spn-rrkjus_psl.1.0.0.UPF',
    'Ca': 'Ca.pbe-n-rrkjus_psl.1.0.0.UPF'
}

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
  ntyp = {ntyp}
  ecutwfc = 80
  ecutrho = 640
  input_dft = 'B3LYP'
  london = .false.
  nspin = {nspin}
  starting_magnetization(1) = {magnetization}
  tot_charge = {charge}
/
&electrons
  conv_thr = 1.0d-8
  mixing_beta = 0.3
  electron_maxstep = 200
/
ATOMIC_SPECIES
  {atom1}  {mass1}  {pseudo1}
  {atom2}  {mass2}  {pseudo2}
  {atom3}  {mass3}  {pseudo3}

CELL_PARAMETERS angstrom
  30.0 0.0 0.0
  0.0 30.0 0.0
  0.0 0.0 30.0

ATOMIC_POSITIONS angstrom
  {atom1}  0.000000  0.000000  0.000000
  {atom2}  {h2x: .6f}  0.000000  0.000000
  {atom3}  {nex: .6f}  0.000000  0.000000

K_POINTS gamma
"""


def write_qe_input(directory: str, m: float, n: float) -> None:
    prefix = f"{ATOM3}{m},{ATOM2}{n}"
    
    # Count different atom types
    unique_atoms = list(set([ATOM1, ATOM2, ATOM3]))
    ntyp = len(unique_atoms)
    
    # Calculate spin and magnetization based on multiplicity
    if MULTIPLICITY == 1:
        nspin = 1
        magnetization = 0.0
    else:
        nspin = 2
        # For multiplicity > 1, calculate magnetization
        # This is a simplified approach - you may need to adjust based on your specific needs
        magnetization = (MULTIPLICITY - 1) / 2.0
    
    content = PW_TEMPLATE.format(
        prefix=prefix, 
        nex=m, 
        h2x=n,
        ntyp=ntyp,
        charge=CHARGE,
        nspin=nspin,
        magnetization=magnetization,
        atom1=ATOM1,
        atom2=ATOM2,
        atom3=ATOM3,
        mass1=ATOMIC_MASSES.get(ATOM1, 1.0),
        mass2=ATOMIC_MASSES.get(ATOM2, 1.0),
        mass3=ATOMIC_MASSES.get(ATOM3, 1.0),
        pseudo1=PSEUDO_FILES.get(ATOM1, f"{ATOM1}.pbe-n-rrkjus_psl.1.0.0.UPF"),
        pseudo2=PSEUDO_FILES.get(ATOM2, f"{ATOM2}.pbe-n-rrkjus_psl.1.0.0.UPF"),
        pseudo3=PSEUDO_FILES.get(ATOM3, f"{ATOM3}.pbe-n-rrkjus_psl.1.0.0.UPF")
    )
    inp_path = os.path.join(directory, "pw.in")
    with open(inp_path, "w") as f:
        f.write(content)


def main() -> None:
    # Create main folder
    if not os.path.exists(MAIN_FOLDER):
        os.makedirs(MAIN_FOLDER)
        print(f"📁 Creating main folder: {MAIN_FOLDER}")
    
    # Enter main folder
    os.chdir(MAIN_FOLDER)
    
    # Counter for creating subfolders
    created_count = 0
    
    for i in range(0, 71):
        for j in range(0, 71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            dirname = f"{ATOM3}{m},{ATOM2}{n}"
            os.makedirs(dirname, exist_ok=True)
            write_qe_input(dirname, m, n)
            
            created_count += 1
            
            # Show progress
            if created_count % 100 == 0:
                print(f"🔄 Created {created_count} folders...")
    
    # Return to parent directory
    os.chdir('..')
    
    print(f"✅ Completed! Created {created_count} calculation folders")
    print(f"📁 All files organized in: {MAIN_FOLDER}/")
    print(f"🔧 Atom configuration: {ATOM1}-{ATOM2}-{ATOM3}")
    print(f"📊 Grid size: 71×71 = 5041 calculation points")
    print()
    print("💡 Usage:")
    print(f"   cd {MAIN_FOLDER}")
    print("   bash ../qe.sh")
    print("   python3 ../read_qe.py")
    print()
    print("QE input has been generated (filename: pw.in). Please place pseudopotentials in ./pseudo directory and create ./tmp for execution.")
    print(f"Required pseudopotential files: {PSEUDO_FILES.get(ATOM1, 'custom')}, {PSEUDO_FILES.get(ATOM2, 'custom')}, {PSEUDO_FILES.get(ATOM3, 'custom')}")


if __name__ == "__main__":
    main()


