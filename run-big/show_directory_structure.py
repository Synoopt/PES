#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Directory structure display script
Shows the directory organization structure of the new three-atom configuration system
"""

import os
from config_reader import get_gaussian_config, get_cp2k_config, get_qe_config

def print_directory_structure():
    """Print directory structure description"""
    print("=" * 80)
    print("📁 Three-Atom Configuration System - Directory Structure Description")
    print("=" * 80)
    print()
    
    # Get current configuration
    try:
        gaussian_config = get_gaussian_config()
        cp2k_config = get_cp2k_config()
        qe_config = get_qe_config()
        
        print("🔧 Current atom configuration:")
        print(f"   Gaussian: {gaussian_config[0]}-{gaussian_config[1]}-{gaussian_config[2]}")
        print(f"   CP2K:     {cp2k_config[0]}-{cp2k_config[1]}-{cp2k_config[2]}")
        print(f"   QE:       {qe_config[0]}-{qe_config[1]}-{qe_config[2]}")
        print()
        
        # Generate main folder names
        gaussian_main = f"{gaussian_config[0]}_{gaussian_config[1]}_{gaussian_config[2]}_gaussian_calculations"
        cp2k_main = f"{cp2k_config[0]}_{cp2k_config[1]}_{cp2k_config[2]}_cp2k_calculations"
        qe_main = f"{qe_config[0]}_{qe_config[1]}_{qe_config[2]}_qe_calculations"
        
        print("📁 Directory structure:")
        print("run-big/")
        print("├── 📄 Configuration files")
        print("│   ├── atom_config.py                    # Unified atom configuration")
        print("│   ├── config_reader.py                  # Configuration reading module")
        print("│   ├── atom_config_examples.py           # Configuration examples")
        print("│   └── test_atom_config.py               # Test script")
        print("│")
        print("├── 📄 Generation scripts")
        print("│   ├── generate_gaussian_input.py        # Gaussian input generation")
        print("│   ├── generate_cp2k_input.py            # CP2K input generation")
        print("│   └── generate_qe_input.py              # QE input generation")
        print("│")
        print("├── 📄 Execution scripts")
        print("│   ├── g09.sh                            # Gaussian execution (auto-detect version)")
        print("│   ├── cp2k.sh                           # CP2K execution")
        print("│   └── qe.sh                             # QE execution")
        print("│")
        print("├── 📄 Result extraction scripts")
        print("│   ├── read.py                           # Traditional Gaussian result extraction")
        print("│   ├── read_gaussian.py                  # Modern Gaussian result extraction")
        print("│   ├── read_cp2k.py                      # CP2K result extraction")
        print("│   └── read_qe.py                        # QE result extraction")
        print("│")
        print("├── 📄 Utility scripts")
        print("│   ├── quick_start.py                    # Quick start")
        print("│   └── show_directory_structure.py       # This script")
        print("│")
        print("├── 📁 Pseudopotential files")
        print("│   └── pseudo/                           # QE pseudopotential files")
        print("│")
        print("└── 📁 Calculation results (generated after execution)")
        print("    ├── " + gaussian_main + "/")
        print("    │   ├── Ne0.5,H-0.5/")
        print("    │   │   ├── Ne0.5,H-0.5.gjf")
        print("    │   │   └── Ne0.5,H-0.5.out")
        print("    │   ├── Ne0.55,H-0.55/")
        print("    │   │   ├── Ne0.55,H-0.5.gjf")
        print("    │   │   └── Ne0.55,H-0.5.out")
        print("    │   └── ...")
        print("    │")
        print("    ├── " + cp2k_main + "/")
        print("    │   ├── Ne0.5,H-0.5/")
        print("    │   │   ├── cp2k.inp")
        print("    │   │   └── cp2k.out")
        print("    │   └── ...")
        print("    │")
        print("    └── " + qe_main + "/")
        print("        ├── Ne0.5,H-0.5/")
        print("        │   ├── pw.in")
        print("        │   └── pw.out")
        print("        └── ...")
        print()
        
        print("🆕 Advantages of new directory structure:")
        print("   ✅ Clearer organization: independent folders for each software")
        print("   ✅ Easy management: can backup/delete separately")
        print("   ✅ Avoid confusion: different software outputs don't mix together")
        print("   ✅ Convenient analysis: can process results separately")
        print()
        
        print("💡 Usage:")
        print("   1. Configure atom types: modify atom_config.py or generate_*.py")
        print("   2. Generate input files: python3 generate_*.py")
        print("   3. Enter calculation directory: cd " + gaussian_main)
        print("   4. Run calculations: bash ../g09.sh")
        print("   5. Extract results: python3 ../read_*.py")
        print()
        
        # Check actually existing directories
        print("🔍 Check existing directories:")
        existing_dirs = []
        for main_dir in [gaussian_main, cp2k_main, qe_main]:
            if os.path.exists(main_dir):
                existing_dirs.append(main_dir)
                print(f"   ✅ {main_dir}")
            else:
                print(f"   ❌ {main_dir} (not created)")
        
        if existing_dirs:
            print(f"\n📊 Created {len(existing_dirs)} main folders")
        else:
            print("\n⚠️  No calculation folders created yet")
            print("   Please run generate_*.py scripts first")
        
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        print("Please ensure config_reader.py file exists and configuration is correct")

def show_file_counts():
    """Display file counts in each directory"""
    print("\n" + "=" * 80)
    print("📊 File statistics")
    print("=" * 80)
    
    try:
        gaussian_config = get_gaussian_config()
        cp2k_config = get_cp2k_config()
        qe_config = get_qe_config()
        
        # Check each main folder
        configs = [
            ("Gaussian", gaussian_config, f"{gaussian_config[0]}_{gaussian_config[1]}_{gaussian_config[2]}_gaussian_calculations"),
            ("CP2K", cp2k_config, f"{cp2k_config[0]}_{cp2k_config[1]}_{cp2k_config[2]}_cp2k_calculations"),
            ("QE", qe_config, f"{qe_config[0]}_{qe_config[1]}_{qe_config[2]}_qe_calculations")
        ]
        
        for software, config, main_dir in configs:
            print(f"\n🔍 {software} ({config[0]}-{config[1]}-{config[2]}):")
            if os.path.exists(main_dir):
                # Count subfolders
                subdirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d)) and ',' in d]
                print(f"   📁 Main folder: {main_dir}")
                print(f"   📊 Calculation subfolders: {len(subdirs)}")
                
                # Count input files
                input_files = 0
                output_files = 0
                for subdir in subdirs[:5]:  # Only check first 5 folders as example
                    subdir_path = os.path.join(main_dir, subdir)
                    for file in os.listdir(subdir_path):
                        if file.endswith(('.gjf', '.inp', '.in')):
                            input_files += 1
                        elif file.endswith('.out'):
                            output_files += 1
                
                print(f"   📄 Input files: {input_files} (example)")
                print(f"   📄 Output files: {output_files} (example)")
                
                if len(subdirs) > 5:
                    print(f"   ... and {len(subdirs) - 5} more folders")
            else:
                print(f"   ❌ Main folder doesn't exist: {main_dir}")
    
    except Exception as e:
        print(f"❌ Error counting files: {e}")

if __name__ == "__main__":
    print_directory_structure()
    show_file_counts()
    
    print("\n" + "=" * 80)
    print("🎯 Summary")
    print("=" * 80)
    print("The new directory structure makes your calculation projects more organized!")
    print("Each software's calculation results have independent folders, making management and analysis easier.")
    print("To modify atom configuration, simply edit atom_config.py or corresponding generate_*.py files.")
