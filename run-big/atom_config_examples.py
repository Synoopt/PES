#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atom configuration examples file
Shows how to configure different atom combinations in the three generate scripts
"""

# ============================================================================
# Example 1: Default configuration - H-H-Ne system
# ============================================================================
DEFAULT_CONFIG = {
    'ATOM1': 'H',    # First atom type
    'ATOM2': 'H',    # Second atom type  
    'ATOM3': 'Ne',   # Third atom type
    'description': 'Hydrogen-Hydrogen-Neon system (default configuration)',
    'directory_example': 'Ne0.5,H-0.5'
}

# ============================================================================
# Example 2: Organic molecular system - C-H-O system
# ============================================================================
ORGANIC_CONFIG = {
    'ATOM1': 'C',    # Carbon atom
    'ATOM2': 'H',    # Hydrogen atom
    'ATOM3': 'O',    # Oxygen atom
    'description': 'Carbon-Hydrogen-Oxygen system (organic molecule)',
    'directory_example': 'O0.5,H-0.5'
}

# ============================================================================
# Example 3: Alkali metal system - Li-Na-K system
# ============================================================================
ALKALI_CONFIG = {
    'ATOM1': 'Li',   # Lithium atom
    'ATOM2': 'Na',   # Sodium atom
    'ATOM3': 'K',    # Potassium atom
    'description': 'Lithium-Sodium-Potassium system (alkali metals)',
    'directory_example': 'K0.5,Na-0.5'
}

# ============================================================================
# Example 4: Halogen system - F-Cl-Br system
# ============================================================================
HALOGEN_CONFIG = {
    'ATOM1': 'F',    # Fluorine atom
    'ATOM2': 'Cl',   # Chlorine atom
    'ATOM3': 'Br',   # Bromine atom
    'description': 'Fluorine-Chlorine-Bromine system (halogens)',
    'directory_example': 'Br0.5,Cl-0.5'
}

# ============================================================================
# Example 5: Noble gas system - He-Ne-Ar system
# ============================================================================
NOBLE_GAS_CONFIG = {
    'ATOM1': 'He',   # Helium atom
    'ATOM2': 'Ne',   # Neon atom
    'ATOM3': 'Ar',   # Argon atom
    'description': 'Helium-Neon-Argon system (noble gases)',
    'directory_example': 'Ar0.5,Ne-0.5'
}

# ============================================================================
# Usage instructions
# ============================================================================
def print_usage():
    """Print usage instructions"""
    print("=" * 60)
    print("Three-Atom Configuration Usage")
    print("=" * 60)
    print()
    print("1. Choose the atom combination you need")
    print("2. Copy the corresponding configuration to the beginning of generate_*.py files")
    print("3. Ensure corresponding basis set/pseudopotential files exist")
    print("4. Run scripts to generate input files")
    print()
    print("Example configurations:")
    print()

def print_config(config, name):
    """Print configuration information"""
    print(f"【{name}】")
    print(f"Description: {config['description']}")
    print(f"Configuration:")
    print(f"  ATOM1 = '{config['ATOM1']}'    # First atom type")
    print(f"  ATOM2 = '{config['ATOM2']}'    # Second atom type")
    print(f"  ATOM3 = '{config['ATOM3']}'    # Third atom type")
    print(f"Directory example: {config['directory_example']}")
    print()

if __name__ == "__main__":
    print_usage()
    
    print_config(DEFAULT_CONFIG, "Default Configuration")
    print_config(ORGANIC_CONFIG, "Organic Molecule Configuration")
    print_config(ALKALI_CONFIG, "Alkali Metal Configuration")
    print_config(HALOGEN_CONFIG, "Halogen Configuration")
    print_config(NOBLE_GAS_CONFIG, "Noble Gas Configuration")
    
    print("=" * 60)
    print("Important Notes:")
    print("- After modifying atom types, ensure corresponding basis set/pseudopotential files exist")
    print("- Recommend testing new configurations with small grids first")
    print("- Some atom combinations may require adjustment of calculation parameters")
    print("=" * 60)
