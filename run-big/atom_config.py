#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified atom configuration file
Modify atom types here, all scripts will automatically use the same configuration
"""

# Unified atom configuration file
# Modify atom types here, all scripts will automatically use the same configuration

# Atom Configuration - Modify the atom combination you need here
# Default configuration: H-H-Ne system
ATOM1 = 'H' # First atom type
ATOM2 = 'H' # Second atom type  
ATOM3 = 'Ne' # Third atom type

# ⚡ Charge and Multiplicity Configuration
CHARGE = 1      # Total charge (0 = neutral, 1 = +1, -1 = -1, etc.)
MULTIPLICITY = 2  # Spin multiplicity (1 = singlet, 2 = doublet, 3 = triplet, etc.)

# Preset Configuration Examples (uncomment to use)
# Organic molecular system
# ATOM1 = 'C' # Carbon atom
# ATOM2 = 'H' # Hydrogen atom
# ATOM3 = 'O' # Oxygen atom
# CHARGE = 0  # Neutral molecule
# MULTIPLICITY = 1  # Singlet state
 
# Alkali metal system
# ATOM1 = 'Li' # Lithium atom
# ATOM2 = 'Na' # Sodium atom
# ATOM3 = 'K'  # Potassium atom
# CHARGE = 1  # +1 charge
# MULTIPLICITY = 2  # Doublet state

# Halogen system
# ATOM1 = 'F'  # Fluorine atom
# ATOM2 = 'Cl' # Chlorine atom
# ATOM3 = 'Br' # Bromine atom
# CHARGE = -1 # -1 charge
# MULTIPLICITY = 2  # Doublet state

# Noble gas system
# ATOM1 = 'He' # Helium atom
# ATOM2 = 'Ne' # Neon atom
# ATOM3 = 'Ar' # Argon atom
# CHARGE = 0  # Neutral
# MULTIPLICITY = 1  # Singlet state

# ============================================================================
# Supported Atom Types List
# ============================================================================
SUPPORTED_ATOMS = [
    'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca'
]

# ============================================================================
# Configuration Validation Functions
# ============================================================================
def validate_config():
    """Validate if atom configuration is valid"""
    errors = []
    
    # Check if atom types are supported
    for atom in [ATOM1, ATOM2, ATOM3]:
        if atom not in SUPPORTED_ATOMS:
            errors.append(f"Unsupported atom type: {atom}")
    
    # Check for duplicate atoms
    if len(set([ATOM1, ATOM2, ATOM3])) < 3:
        errors.append("Three atom types must be different")
    
    # Check if atom types are empty
    if not all([ATOM1, ATOM2, ATOM3]):
        errors.append("Atom types cannot be empty")
    
    return errors

def print_config():
    """Print current configuration information"""
    print("=" * 60)
    print("Current Atom Configuration")
    print("=" * 60)
    print(f"ATOM1 = '{ATOM1}'    # First atom type")
    print(f"ATOM2 = '{ATOM2}'    # Second atom type")
    print(f"ATOM3 = '{ATOM3}'    # Third atom type")
    print()
    print(f"Directory naming format: {ATOM3}{{m}},{ATOM2}{{n}}")
    print(f"Example directory: {ATOM3}0.5,{ATOM2}-0.5")
    print()
    
    # Validate configuration
    errors = validate_config()
    if errors:
        print("⚠️  Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print()
        return False
    else:
        print("✅ Configuration validation passed")
        print()
        return True

def get_output_filenames(software):
    """Get output filenames"""
    base_name = f"{ATOM1.lower()}_{ATOM2.lower()}_{ATOM3.lower()}"
    
    if software == "gaussian":
        return {
            "energy": f"{base_name}_gaussian_energy.xlsx",
            "errors": f"{base_name}_gaussian_errors.xlsx"
        }
    elif software == "cp2k":
        return {
            "energy": f"{base_name}_cp2k_energy.xlsx",
            "errors": f"{base_name}_cp2k_errors.xlsx"
        }
    elif software == "qe":
        return {
            "energy": f"{base_name}_qe_energy.xlsx",
            "errors": f"{base_name}_qe_errors.xlsx"
        }
    elif software == "legacy":
        return {
            "energy": f"{base_name}_input_force.xlsx",
            "errors": f"{base_name}_errors.xlsx"
        }
    else:
        return {
            "energy": f"{base_name}_{software}_energy.xlsx",
            "errors": f"{base_name}_{software}_errors.xlsx"
        }

# ============================================================================
# Usage Instructions
# ============================================================================
def print_usage():
    """Print usage instructions"""
    print("=" * 60)
    print("Atom Configuration File Usage Instructions")
    print("=" * 60)
    print()
    print("1. Modify ATOM1, ATOM2, ATOM3 variables at the beginning of this file")
    print("2. Save the file")
    print("3. Run any generate_*.py or read_*.py script")
    print("4. All scripts will automatically use the same atom configuration")
    print()
    print("Supported atom types:")
    print(", ".join(SUPPORTED_ATOMS))
    print()
    print("Important notes:")
    print("- Ensure corresponding basis set/pseudopotential files exist")
    print("- Recommend testing new configurations with small grids first")
    print("- Some atom combinations may require adjustment of calculation parameters")

# ============================================================================
# Test Functions
# ============================================================================
def test_config():
    """Test current configuration"""
    print("Testing atom configuration...")
    
    if print_config():
        print("🎉 Configuration test passed!")
        print("Now you can run generate_*.py and read_*.py scripts.")
        return True
    else:
        print("❌ Configuration test failed!")
        print("Please check and correct configuration errors.")
        return False

if __name__ == "__main__":
    print_usage()
    print()
    test_config()
