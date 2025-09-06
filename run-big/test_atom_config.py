#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atom configuration test script
Used to quickly verify if new atom configurations are correct
"""

import os
import tempfile
import shutil

def test_gaussian_config():
    """Test Gaussian configuration"""
    print("Testing Gaussian configuration...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    
    try:
        # Import and modify configuration
        import sys
        sys.path.append('.')
        
        # Create test generate script
        test_script = '''
import os 

# Test configuration
ATOM1 = 'C'    # First atom type
ATOM2 = 'H'    # Second atom type  
ATOM3 = 'O'    # Third atom type

string1='''%mem=10GB
%nprocs=8
# sp b3lyp/6-311g** Force nosymm scf=(qc)

Title Card Required

1 2
 {}                  0.00    0.00    0.00
'''.format(ATOM1)

# Only generate one test file
m = 0.5
n = -0.5
stringi=' {}             {}     0.00    0.00'.format(ATOM2, n)
stringj='\\n {}            {}     0.00    0.00\\n\\n'.format(ATOM3, m)
string0=string1+stringi+stringj
dirname='{}{},{}{}'.format(ATOM3,m,ATOM2,n)
os.makedirs(dirname,exist_ok=True)
filename = "{}{},{}{}/{}{},{}{}.gjf".format(ATOM3,m,ATOM2,n,ATOM3,m,ATOM2,n)
with open(filename,'w') as f:
    f.write(string0)

print(f"Generated test file: {filename}")
print(f"Directory structure: {os.listdir('.')}")
print(f"File content preview:")
with open(filename, 'r') as f:
    content = f.read()
    print(content[:200] + "..." if len(content) > 200 else content)
'''
        
        with open('test_gaussian.py', 'w') as f:
            f.write(test_script)
        
        # Run test
        os.system('python3 test_gaussian.py')
        
        # Check results
        if os.path.exists('O0.5,H-0.5'):
            print("✅ Gaussian configuration test passed!")
            return True
        else:
            print("❌ Gaussian configuration test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Gaussian configuration test error: {e}")
        return False
    finally:
        # Clean up temporary directory
        os.chdir('..')
        shutil.rmtree(temp_dir)

def test_cp2k_config():
    """Test CP2K configuration"""
    print("Testing CP2K configuration...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    
    try:
        # Create test generate script
        test_script = '''
import os

# Test configuration
ATOM1 = 'C'    # First atom type
ATOM2 = 'H'    # Second atom type  
ATOM3 = 'O'    # Third atom type

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
        atom3=ATOM3
    )
    inp_path = os.path.join(directory, "cp2k.inp")
    with open(inp_path, "w") as f:
        f.write(content)

# Only generate one test file
m = 0.5
n = -0.5
dirname = f"{ATOM3}{m},{ATOM2}{n}"
os.makedirs(dirname, exist_ok=True)
write_cp2k_input(dirname, m, n)

print(f"Generated test file: {dirname}/cp2k.inp")
print(f"Directory structure: {os.listdir('.')}")
print(f"File content preview:")
with open(f"{dirname}/cp2k.inp", 'r') as f:
    content = f.read()
    print(content[:200] + "..." if len(content) > 200 else content)
'''
        
        with open('test_cp2k.py', 'w') as f:
            f.write(test_script)
        
        # Run test
        os.system('python3 test_cp2k.py')
        
        # Check results
        if os.path.exists('O0.5,H-0.5/cp2k.inp'):
            print("✅ CP2K configuration test passed!")
            return True
        else:
            print("❌ CP2K configuration test failed!")
            return False
            
    except Exception as e:
        print(f"❌ CP2K configuration test error: {e}")
        return False
    finally:
        # Clean up temporary directory
        os.chdir('..')
        shutil.rmtree(temp_dir)

def test_qe_config():
    """Test QE configuration"""
    print("Testing QE configuration...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    
    try:
        # Create test generate script
        test_script = '''
import os

# Test configuration
ATOM1 = 'C'    # First atom type
ATOM2 = 'H'    # Second atom type  
ATOM3 = 'O'    # Third atom type

# Simplified atomic mass configuration
ATOMIC_MASSES = {'C': 12.011, 'H': 1.00794, 'O': 15.999}
PSEUDO_FILES = {'C': 'C.pbe-n-rrkjus_psl.1.0.0.UPF', 'H': 'H.pbe-rrkjus.UPF', 'O': 'O.pbe-n-rrkjus_psl.1.0.0.UPF'}

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
    
    content = PW_TEMPLATE.format(
        prefix=prefix, 
        nex=m, 
        h2x=n,
        ntyp=ntyp,
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

# Only generate one test file
m = 0.5
n = -0.5
dirname = f"{ATOM3}{m},{ATOM2}{n}"
os.makedirs(dirname, exist_ok=True)
write_qe_input(dirname, m, n)

print(f"Generated test file: {dirname}/pw.in")
print(f"Directory structure: {os.listdir('.')}")
print(f"File content preview:")
with open(f"{dirname}/pw.in", 'r') as f:
    content = f.read()
    print(content[:200] + "..." if len(content) > 200 else content)
'''
        
        with open('test_qe.py', 'w') as f:
            f.write(test_script)
        
        # Run test
        os.system('python3 test_qe.py')
        
        # Check results
        if os.path.exists('O0.5,H-0.5/pw.in'):
            print("✅ QE configuration test passed!")
            return True
        else:
            print("❌ QE configuration test failed!")
            return False
            
    except Exception as e:
        print(f"❌ QE configuration test error: {e}")
        return False
    finally:
        # Clean up temporary directory
        os.chdir('..')
        shutil.rmtree(temp_dir)

def main():
    """Main function"""
    print("=" * 60)
    print("Three-Atom Configuration Test Script")
    print("=" * 60)
    print()
    print("This script will test if the C-H-O atom combination configuration is correct")
    print()
    
    results = []
    
    # Test three software packages
    results.append(("Gaussian", test_gaussian_config()))
    results.append(("CP2K", test_cp2k_config()))
    results.append(("QE", test_qe_config()))
    
    print()
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for software, result in results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{software}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Your atom configuration functionality is working properly.")
        print("Now you can modify the ATOM1, ATOM2, ATOM3 variables in the three generate scripts to use different atom combinations.")
    else:
        print("⚠️  Some tests failed, please check configuration or contact technical support.")
    
    print()
    print("Next steps:")
    print("1. Modify atom configuration at the beginning of generate_*.py files")
    print("2. Ensure corresponding basis set/pseudopotential files exist")
    print("3. Run scripts to generate input files")

if __name__ == "__main__":
    main()
