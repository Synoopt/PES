import os 

# Import configuration from unified config file
try:
    from atom_config import ATOM1, ATOM2, ATOM3, CHARGE, MULTIPLICITY
    print(f"Loaded configuration from atom_config.py: {ATOM1}-{ATOM2}-{ATOM3}, Charge={CHARGE}, Multiplicity={MULTIPLICITY}")
except ImportError:
    # Fallback configuration if atom_config.py is not available
    print("atom_config.py not found, using default configuration")
    ATOM1 = 'H'    # First atom type
    ATOM2 = 'H'    # Second atom type  
    ATOM3 = 'Ne'   # Third atom type
    CHARGE = 1      # Total charge (0 = neutral, 1 = +1, -1 = -1, etc.)
    MULTIPLICITY = 2  # Spin multiplicity (1 = singlet, 2 = doublet, 3 = triplet, etc.)

# Create main folder name
MAIN_FOLDER = f"{ATOM1}_{ATOM2}_{ATOM3}_gaussian_calculations"

string1='''%mem=10GB
%nprocs=8
# sp b3lyp/6-311g** Force nosymm scf=(qc)

Title Card Required

{} {}
 {}                  0.00    0.00    0.00
'''.format(CHARGE, MULTIPLICITY, ATOM1)

def main():
    # Create main folder
    if not os.path.exists(MAIN_FOLDER):
        os.makedirs(MAIN_FOLDER)
        print(f"Creating main folder: {MAIN_FOLDER}")
    
    # Enter main folder
    os.chdir(MAIN_FOLDER)
    
    # Counter for creating subfolders
    created_count = 0
    
    for i in range(0,71):
        for j in range(0,71):
            m=round(0.5+0.05*i,6)
            n=round(-0.5-0.05*j,6)
            stringi=' {}             {}     0.00    0.00'.format(ATOM2, n)
            stringj='\n {}            {}     0.00    0.00\n\n'.format(ATOM3, m)
            string0=string1+stringi+stringj
            
            # Create subfolder
            subfolder_name = '{}{},{}{}'.format(ATOM3,m,ATOM2,n)
            os.makedirs(subfolder_name, exist_ok=True)
            
            # Create input file
            filename = "{}{},{}{}/{}{},{}{}.gjf".format(ATOM3,m,ATOM2,n,ATOM3,m,ATOM2,n)
            with open(filename, 'w') as f:
                f.write(string0)
            
            created_count += 1
            
            # Show progress
            if created_count % 100 == 0:
                print(f"🔄 Created {created_count} folders...")
    
    # Return to parent directory
    os.chdir('..')
    
    print(f"Completed! Created {created_count} calculation folders")
    print(f"All files organized in: {MAIN_FOLDER}/")
    print(f"Atom configuration: {ATOM1}-{ATOM2}-{ATOM3}")
    print(f"Grid size: 71×71 = 5041 calculation points")
    print()
    print("💡 Usage:")
    print(f"   cd {MAIN_FOLDER}")
    print("   bash ../g09.sh")
    print("   python3 ../read_gaussian.py")

if __name__ == "__main__":
    main()


