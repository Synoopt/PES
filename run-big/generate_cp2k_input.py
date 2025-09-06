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
MAIN_FOLDER = f"{ATOM1}_{ATOM2}_{ATOM3}_cp2k_calculations"

HEADER_TEMPLATE = """
&GLOBAL
  PROJECT {project}
  RUN_TYPE ENERGY_FORCE
&END GLOBAL

&FORCE_EVAL
  METHOD QUICKSTEP
  &DFT
    CHARGE {charge}
    UKS TRUE
    MULTIPLICITY {multiplicity}

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
      {atom1}   0.000000  0.000000  0.000000
      {atom2}   {h2x: .6f}  0.000000  0.000000
      {atom3}   {nex: .6f}  0.000000  0.000000
    &END COORD

    &KIND {atom1}
      BASIS_SET TZV2P-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
    &KIND {atom2}
      BASIS_SET TZV2P-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
    &KIND {atom3}
      BASIS_SET TZV2P-MOLOPT-GTH
      POTENTIAL GTH-PBE
    &END KIND
  &END SUBSYS

  &PRINT
    &FORCES
      &EACH
        GEO_OPT 1
        MD 1
      &END EACH
    &END FORCES
  &END PRINT
&END FORCE_EVAL
"""


def write_cp2k_input(directory: str, m: float, n: float) -> None:
    project = f"{ATOM3}{m},{ATOM2}{n}"
    content = HEADER_TEMPLATE.format(
        project=project, 
        nex=m, 
        h2x=n,
        atom1=ATOM1,
        atom2=ATOM2,
        atom3=ATOM3,
        charge=CHARGE,
        multiplicity=MULTIPLICITY
    )
    inp_path = os.path.join(directory, "cp2k.inp")
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
            write_cp2k_input(dirname, m, n)
            
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
    print("   bash ../cp2k.sh")
    print("   bash ../cp2k.sh")
    print("   python3 ../read_cp2k.py")
    print()
    print("CP2K input has been generated (filename: cp2k.inp). Please ensure the following files are available and visible in the CP2K runtime environment:")
    print("- BASIS_MOLOPT (usually distributed with CP2K, such as data/BASIS_MOLOPT)")
    print("- GTH_POTENTIALS (usually distributed with CP2K, such as data/GTH_POTENTIALS)")


if __name__ == "__main__":
    main()


