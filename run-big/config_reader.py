#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal configuration reading module
Automatically reads atom configuration from generate files to avoid duplicate configuration
"""

import re
import os

def get_atom_config_from_generate(generate_file):
    """
    Read atom configuration from specified generate file
    
    Args:
        generate_file (str): generate filename, such as 'generate_gaussian_input.py'
    
    Returns:
        tuple: (ATOM1, ATOM2, ATOM3) atom configuration
    """
    try:
        # Read generate file content
        with open(generate_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract ATOM1, ATOM2, ATOM3 values
        atom1_match = re.search(r"ATOM1\s*=\s*['\"]([^'\"]+)['\"]", content)
        atom2_match = re.search(r"ATOM2\s*=\s*['\"]([^'\"]+)['\"]", content)
        atom3_match = re.search(r"ATOM3\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        if atom1_match and atom2_match and atom3_match:
            atom1 = atom1_match.group(1)
            atom2 = atom2_match.group(1)
            atom3 = atom3_match.group(1)
            print(f"✅ Configuration read from {generate_file}: {atom1}-{atom2}-{atom3}")
            return atom1, atom2, atom3
        else:
            print(f"⚠️  Unable to read complete configuration from {generate_file}, using default configuration")
            return 'H', 'H', 'Ne'
            
    except FileNotFoundError:
        print(f"⚠️  Cannot find {generate_file} file, using default configuration")
        return 'H', 'H', 'Ne'
    except Exception as e:
        print(f"⚠️  Error reading configuration from {generate_file}: {e}, using default configuration")
        return 'H', 'H', 'Ne'

def get_atom_config_by_software(software):
    """
    Automatically select corresponding generate file based on software type and read configuration
    
    Args:
        software (str): Software name, such as 'gaussian', 'cp2k', 'qe'
    
    Returns:
        tuple: (ATOM1, ATOM2, ATOM3) atom configuration
    """
    file_mapping = {
        'gaussian': 'generate_gaussian_input.py',
        'cp2k': 'generate_cp2k_input.py',
        'qe': 'generate_qe_input.py',
        'quantum_espresso': 'generate_qe_input.py'
    }
    
    if software.lower() in file_mapping:
        generate_file = file_mapping[software.lower()]
        return get_atom_config_from_generate(generate_file)
    else:
        print(f"⚠️  Unsupported software type: {software}, using default configuration")
        return 'H', 'H', 'Ne'

def get_main_folder_name(atom1, atom2, atom3, software):
    """
    Generate main folder name based on atom configuration and software type
    
    Args:
        atom1, atom2, atom3 (str): Three atom types
        software (str): Software name
    
    Returns:
        str: Main folder name
    """
    software_suffix = {
        'gaussian': 'gaussian_calculations',
        'cp2k': 'cp2k_calculations',
        'qe': 'qe_calculations',
        'quantum_espresso': 'qe_calculations'
    }
    
    suffix = software_suffix.get(software.lower(), 'calculations')
    return f"{atom1}_{atom2}_{atom3}_{suffix}"

def find_calculation_folders(atom1, atom2, atom3, software):
    """
    Find calculation folders, supports new directory structure
    
    Args:
        atom1, atom2, atom3 (str): Three atom types
        software (str): Software name
    
    Returns:
        list: List of calculation folder paths
    """
    main_folder = get_main_folder_name(atom1, atom2, atom3, software)
    
    # First check if main folder exists
    if os.path.exists(main_folder):
        print(f"📁 Found main folder: {main_folder}")
        # Look for calculation subfolders in main folder
        calculation_folders = []
        for item in os.listdir(main_folder):
            item_path = os.path.join(main_folder, item)
            if os.path.isdir(item_path) and ',' in item:  # Calculation folders usually contain commas
                calculation_folders.append(item_path)
        return calculation_folders
    else:
        print(f"⚠️  Main folder not found: {main_folder}")
        # Fallback to old directory structure
        print("🔄 Trying to use old directory structure...")
        calculation_folders = []
        for item in os.listdir('.'):
            if os.path.isdir(item) and ',' in item and item.startswith(f"{atom3}"):
                calculation_folders.append(item)
        return calculation_folders

def validate_atom_config(atom1, atom2, atom3):
    """
    Validate if atom configuration is valid
    
    Args:
        atom1, atom2, atom3 (str): Three atom types
    
    Returns:
        bool: Whether configuration is valid
    """
    # Supported atom types list
    supported_atoms = [
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca'
    ]
    
    errors = []
    
    # Check if atom types are supported
    for atom in [atom1, atom2, atom3]:
        if atom not in supported_atoms:
            errors.append(f"Unsupported atom type: {atom}")
    
    # Check for duplicate atoms
    if len(set([atom1, atom2, atom3])) < 3:
        errors.append("Three atom types must be different")
    
    # Check if atom types are empty
    if not all([atom1, atom2, atom3]):
        errors.append("Atom types cannot be empty")
    
    if errors:
        print("⚠️  Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Atom configuration validation passed")
        return True

def get_output_filename(atom1, atom2, atom3, software, file_type):
    """
    Generate output filename based on atom configuration and software type
    
    Args:
        atom1, atom2, atom3 (str): Three atom types
        software (str): Software name
        file_type (str): File type, such as 'energy', 'errors'
    
    Returns:
        str: Complete output filename
    """
    base_name = f"{atom1.lower()}_{atom2.lower()}_{atom3.lower()}"
    
    if software.lower() == "gaussian":
        return f"{base_name}_gaussian_{file_type}.csv"
    elif software.lower() == "cp2k":
        return f"{base_name}_cp2k_{file_type}.csv"
    elif software.lower() == "qe":
        return f"{base_name}_qe_{file_type}.csv"
    elif software.lower() == "legacy":
        if file_type == "energy":
            return f"{base_name}_input_force.csv"
        else:
            return f"{base_name}_{file_type}.csv"
    else:
        return f"{base_name}_{software}_{file_type}.csv"

# Convenience functions: directly get configuration for each software
def get_gaussian_config():
    """Get Gaussian atom configuration"""
    return get_atom_config_by_software('gaussian')

# Convenience functions: directly get configuration for each software
def get_cp2k_config():
    """Get CP2K atom configuration"""
    return get_atom_config_by_software('cp2k')

# Convenience functions: directly get configuration for each software
def get_qe_config():
    """Get QE atom configuration"""
    return get_atom_config_by_software('qe')

if __name__ == "__main__":
    print("=" * 60)
    print("Configuration Reading Module Test")
    print("=" * 60)
    
    # Test reading configuration from different files
    print("\n1. Testing reading configuration from Gaussian file:")
    gaussian_config = get_gaussian_config()
    validate_atom_config(*gaussian_config)
    
    print("\n2. Testing reading configuration from CP2K file:")
    cp2k_config = get_cp2k_config()
    validate_atom_config(*cp2k_config)
    
    print("\n3. Testing reading configuration from QE file:")
    qe_config = get_qe_config()
    validate_atom_config(*qe_config)
    
    print("\n4. Testing output filename generation:")
    for software in ['gaussian', 'cp2k', 'qe']:
        energy_file = get_output_filename(*gaussian_config, software, 'energy')
        error_file = get_output_filename(*gaussian_config, software, 'errors')
        print(f"{software}: {energy_file}, {error_file}")
    
    print("\n5. Testing main folder name generation:")
    for software in ['gaussian', 'cp2k', 'qe']:
        main_folder = get_main_folder_name(*gaussian_config, software)
        print(f"{software}: {main_folder}")
    
    print("\n✅ Configuration reading module test completed!")
