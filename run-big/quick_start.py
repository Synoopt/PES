#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick start script
Helps users quickly configure and test the three-atom configuration functionality
"""

import os
import sys

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🎯 Three-Atom Configuration System - Quick Start")
    print("=" * 70)
    print()

def print_menu():
    """Print main menu"""
    print("Please select operation:")
    print("1. 📝 View current atom configuration")
    print("2. ⚙️  Modify atom configuration")
    print("3. 🧪 Test atom configuration")
    print("4. 📁 Generate input files")
    print("5. 📊 Extract calculation results")
    print("6. 📚 View usage instructions")
    print("7. 🚪 Exit")
    print()

def view_config():
    """View current configuration"""
    print("Viewing current configuration...")
    try:
        # Try to import configuration
        sys.path.append('.')
        from atom_config import print_config
        print_config()
    except ImportError:
        print("❌ Cannot import atom_config.py, please check if file exists")
    except Exception as e:
        print(f"❌ Error viewing configuration: {e}")

def modify_config():
    """Modify atom configuration"""
    print("Modifying atom configuration...")
    print()
    print("Please select preset configuration:")
    print("1. H-H-Ne (default, hydrogen-hydrogen-neon)")
    print("2. C-H-O (organic molecule, carbon-hydrogen-oxygen)")
    print("3. Li-Na-K (alkali metals, lithium-sodium-potassium)")
    print("4. F-Cl-Br (halogens, fluorine-chlorine-bromine)")
    print("5. He-Ne-Ar (noble gases, helium-neon-argon)")
    print("6. Custom configuration")
    print("0. Return to main menu")
    print()
    
    choice = input("Please enter choice (0-6): ").strip()
    
    if choice == "0":
        return
    
    configs = {
        "1": ("H", "H", "Ne", "Hydrogen-Hydrogen-Neon system"),
        "2": ("C", "H", "O", "Carbon-Hydrogen-Oxygen system"),
        "3": ("Li", "Na", "K", "Lithium-Sodium-Potassium system"),
        "4": ("F", "Cl", "Br", "Fluorine-Chlorine-Bromine system"),
        "5": ("He", "Ne", "Ar", "Helium-Neon-Argon system")
    }
    
    if choice in configs:
        atom1, atom2, atom3, desc = configs[choice]
        print(f"Selected: {desc}")
        print(f"ATOM1 = {atom1}, ATOM2 = {atom2}, ATOM3 = {atom3}")
        
        confirm = input("Confirm using this configuration? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            update_config_file(atom1, atom2, atom3)
            print("✅ Configuration updated!")
        else:
            print("Configuration not changed")
    
    elif choice == "6":
        custom_config()
    
    else:
        print("❌ Invalid choice")

def custom_config():
    """Custom configuration"""
    print("Custom atom configuration...")
    print()
    print("Supported atom types: H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca")
    print()
    
    atom1 = input("Please enter first atom type (ATOM1): ").strip()
    atom2 = input("Please enter second atom type (ATOM2): ").strip()
    atom3 = input("Please enter third atom type (ATOM3): ").strip()
    
    if atom1 and atom2 and atom3:
        print(f"Configuration: ATOM1 = {atom1}, ATOM2 = {atom2}, ATOM3 = {atom3}")
        confirm = input("Confirm using this configuration? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            update_config_file(atom1, atom2, atom3)
            print("✅ Configuration updated!")
        else:
        print("Configuration not changed")
    else:
        print("❌ Atom types cannot be empty")

def update_config_file(atom1, atom2, atom3):
    """Update configuration file"""
    try:
        # Read original file
        with open('atom_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace atom configuration
        import re
        content = re.sub(r"ATOM1\s*=\s*'[^']*'", f"ATOM1 = '{atom1}'", content)
        content = re.sub(r"ATOM2\s*=\s*'[^']*'", f"ATOM2 = '{atom2}'", content)
        content = re.sub(r"ATOM3\s*=\s*'[^']*'", f"ATOM3 = '{atom3}'", content)
        
        # Write back to file
        with open('atom_config.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ Error updating configuration file: {e}")

def test_config():
    """Test atom configuration"""
    print("Testing atom configuration...")
    try:
        os.system('python3 test_atom_config.py')
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

def generate_input():
    """Generate input files"""
    print("Generating input files...")
    print()
    print("Please select input file type to generate:")
    print("1. Gaussian (.gjf)")
    print("2. CP2K (.inp)")
    print("3. QE (.in)")
    print("4. Generate all")
    print("0. Return to main menu")
    print()
    
    choice = input("Please enter choice (0-4): ").strip()
    
    if choice == "0":
        return
    
    commands = {
        "1": "python3 generate_gaussian_input.py",
        "2": "python3 generate_cp2k_input.py",
        "3": "python3 generate_qe_input.py",
        "4": "python3 generate_gaussian_input.py && python3 generate_cp2k_input.py && python3 generate_qe_input.py"
    }
    
    if choice in commands:
        print(f"Executing: {commands[choice]}")
        os.system(commands[choice])
    else:
        print("❌ Invalid choice")

def extract_results():
    """Extract calculation results"""
    print("Extracting calculation results...")
    print()
    print("Please select result type to extract:")
    print("1. Gaussian results")
    print("2. CP2K results")
    print("3. QE results")
    print("4. Extract all")
    print("0. Return to main menu")
    print()
    
    choice = input("Please enter choice (0-4): ").strip()
    
    if choice == "0":
        return
    
    commands = {
        "1": "python3 read_gaussian.py",
        "2": "python3 read_cp2k.py",
        "3": "python3 read_qe.py",
        "4": "python3 read_gaussian.py && python3 read_cp2k.py && python3 read_qe.py"
    }
    
    if choice in commands:
        print(f"Executing: {commands[choice]}")
        os.system(commands[choice])
    else:
        print("❌ Invalid choice")

def show_help():
    """Show usage instructions"""
    print("Usage instructions...")
    try:
        os.system('python3 atom_config.py')
    except Exception as e:
        print(f"❌ Error showing help: {e}")

def main():
    """Main function"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("Please enter choice (1-7): ").strip()
        
        if choice == "1":
            view_config()
        elif choice == "2":
            modify_config()
        elif choice == "3":
            test_config()
        elif choice == "4":
            generate_input()
        elif choice == "5":
            extract_results()
        elif choice == "6":
            show_help()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please re-enter")
        
        print()
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    main()
