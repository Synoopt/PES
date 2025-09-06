import os
import re
import numpy as np
import pandas as pd

# Use general configuration reading module
try:
    from config_reader import get_qe_config, get_output_filename
    ATOM1, ATOM2, ATOM3 = get_qe_config()
except ImportError:
    # If unable to import config module, use default configuration
    print("⚠️ Unable to import config_reader module, using default configuration")
    ATOM1, ATOM2, ATOM3 = 'H', 'H', 'Ne'

# QE standard SCF output energy line
RY_ENERGY_PATTERN = re.compile(r"!\s+total energy\s*=\s*([-0-9\.Ee\+]+)\s+Ry")


def extract_energy_and_forces_from_qe(output_path: str):
    """
    Extract energy and force information from QE output files
    
    Args:
        output_path (str): QE output file path
    
    Returns:
        tuple: (energy, force1_x, force2_x, force3_x) or (None, None, None, None)
    """
    try:
        with open(output_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return None, None, None, None

    if re.search(r"error|convergence NOT achieved", content, flags=re.IGNORECASE):
        print(f"      ⚠️ File contains error flag or convergence failure")
        return None, None, None, None

    # Extract energy
    energy = None
    matches = RY_ENERGY_PATTERN.findall(content)
    if matches:
        e_ry = float(matches[-1])
        e_ha = e_ry * 0.5  # 1 Ha = 2 Ry
        energy = e_ha
    else:
        # Alternative: some modules only output "total energy = ... Ry" (without !)
        alt = re.findall(r"total energy\s*=\s*([-0-9\.Ee\+]+)\s+Ry", content)
        if alt:
            e_ry = float(alt[-1])
            energy = e_ry * 0.5

    if energy is None:
        return None, None, None, None

    # Extract force information - look for Forces section
    force1_x = None
    force2_x = None
    force3_x = None
    
    # QE forces pattern - look for "Forces acting on atoms" section
    forces_pattern = r"Forces acting on atoms.*?atom\s+1\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+).*?atom\s+2\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+).*?atom\s+3\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)"
    
    forces_match = re.search(forces_pattern, content, re.MULTILINE | re.DOTALL)
    if forces_match:
        # Extract X column force values (1st, 4th, 7th capture groups for X forces)
        force1_x = float(forces_match.group(1))
        force2_x = float(forces_match.group(4))
        force3_x = float(forces_match.group(7))
        print(f"      📊 Extracted force information: F1_x={force1_x:.6f}, F2_x={force2_x:.6f}, F3_x={force3_x:.6f}")
    else:
        # Try alternative QE force format
        print(f"      ⚠️ Standard Forces format not found, trying alternative patterns...")
        
        # Look for force lines in QE output - more flexible pattern
        force_lines = re.findall(r"atom\s+(\d+)\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)\s+([-0-9\.Ee\+]+)", content)
        
        if len(force_lines) >= 3:
            # Take X direction forces of first three atoms
            force1_x = float(force_lines[0][1])  # First atom's X force
            force2_x = float(force_lines[1][1])  # Second atom's X force
            force3_x = float(force_lines[2][1])  # Third atom's X force
            print(f"      📊 Extracted force information: F1_x={force1_x:.6f}, F2_x={force2_x:.6f}, F3_x={force3_x:.6f}")
        else:
            print(f"      ⚠️ Unable to extract force information")

    return energy, force1_x, force2_x, force3_x


def main():
    data_rows = []
    error_rows = []

    for i in range(71):
        for j in range(71):
            m = round(0.5 + 0.05 * i, 6)
            n = round(-0.5 - 0.05 * j, 6)
            # Use dynamic directory naming to match new atom configuration
            dirname = f"{ATOM1}_{ATOM2}_{ATOM3}_qe_calculations/{ATOM3}{m},{ATOM2}{n}"
            out_path = os.path.join(dirname, "pw.out")
            
            print(f"🔄 Processing: {out_path}")
            
            # Extract energy and force information
            energy, force1_x, force2_x, force3_x = extract_energy_and_forces_from_qe(out_path)
            
            if energy is None:
                error_rows.append((m, n))
                print(f"   ❌ Processing failed")
            else:
                # Keep same as original script: y takes -n
                data_row = [m, -n, energy]
                
                # Add force information (if available)
                if force1_x is not None and force2_x is not None and force3_x is not None:
                    data_row.extend([force1_x, force2_x, force3_x])
                    print(f"   ✅ Processing successful: E={energy:.6f}, F1_x={force1_x:.6f}, F2_x={force2_x:.6f}, F3_x={force3_x:.6f}")
                else:
                    # If unable to extract forces, fill with NaN
                    data_row.extend([np.nan, np.nan, np.nan])
                    print(f"   ✅ Processing successful: E={energy:.6f} (force information missing)")
                
                data_rows.append(data_row)

    if data_rows:
        # Determine column names based on whether force information is available
        if len(data_rows[0]) == 6:  # Contains force information
            columns = ["x", "y", "z1", "z2", "z3", "z4"]
            print(f"\n📊 Data contains energy and force information")
        else:
            columns = ["x", "y", "z"]
            print(f"\n📊 Data only contains energy information")
        
        df = pd.DataFrame(data_rows, columns=columns)
        
        try:
            output_filename = get_output_filename(ATOM1, ATOM2, ATOM3, "qe", "energy")
        except:
            output_filename = f"{ATOM1.lower()}_{ATOM2.lower()}_{ATOM3.lower()}_qe_energy.csv"
        
        df.to_csv(output_filename, index=False)
        print(f"✅ Energy and force data saved to: {output_filename}")
        
        # Display data statistics
        print(f"📈 Data statistics:")
        print(f"   Total rows: {len(df)}")
        print(f"   Total columns: {len(df.columns)}")
        if len(data_rows[0]) == 6:
            print(f"   Force information completeness: {sum(1 for row in data_rows if not np.isnan(row[3]))}/{len(df)} ({sum(1 for row in data_rows if not np.isnan(row[3]))/len(df)*100:.1f}%)")

    if error_rows:
        dfe = pd.DataFrame(error_rows, columns=["x", "y"])  # Coordinate pairs (failed)
        try:
            error_filename = get_output_filename(ATOM1, ATOM2, ATOM3, "qe", "errors")
        except:
            error_filename = f"{ATOM1.lower()}_{ATOM2.lower()}_{ATOM3.lower()}_qe_errors.csv"
        dfe.to_csv(error_filename, index=False)
        print(f"❌ Error data saved to: {error_filename}")

    print(f"\n🎯 Processing completed!")
    print(f"   ✅ Success: {len(data_rows)} files")
    print(f"   ❌ Failed: {len(error_rows)} files")
    
    if data_rows and len(data_rows[0]) == 6:
        print(f"   📊 Output format: x, y, z(energy), force1_x, force2_x, force3_x")
        print(f"   💡 Force units: Hartrees/Bohr")


if __name__ == "__main__":
    main()


