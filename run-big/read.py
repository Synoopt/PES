import os
import numpy as np
import pandas as pd
import re

# Use general configuration reading module
try:
    from config_reader import get_gaussian_config, get_output_filename
    ATOM1, ATOM2, ATOM3 = get_gaussian_config()
except ImportError:
    # If unable to import config module, use default configuration
    print("⚠️  Unable to import config_reader module, using default configuration")
    ATOM1, ATOM2, ATOM3 = 'H', 'H', 'Ne'

global X,y,z

def extract_data_from_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        lines=str(lines)
        read0=re.findall('Error',lines)
        if read0 !=[]:
            return []
        else:
            read1=re.findall('1        1         .{0,11}',lines)[-1][20:32]
            read2=re.findall('2        1         .{0,11}',lines)[-1][20:32]
            read3=re.findall('3       10         .{0,11}',lines)[-1][20:32] 
            read4=re.findall('HF=.{0,9}',lines)[-1][3:14]
            read=[read4,read1,read2,read3]
            return read
    

def main():
    X=np.zeros(1)
    Xe=np.zeros(1)
    y=np.zeros(1)
    ye=np.zeros(1)
    z1=np.zeros(1)
    #z2=np.zeros(1)
    #z3=np.zeros(1)
    #z4=np.zeros(1)
    for i in range(71):  # 0 to 40
        for j in range(71):  # 0 to 40
            m=round(0.5+0.05*i,6)
            n=round(-0.5-0.05*j,6)
            # Use dynamic directory naming to match new atom configuration
            dirname = f"{ATOM3}{m},{ATOM2}{n}"
            filename = f"{ATOM3}{m},{ATOM2}{n}.out"
            filepath = os.path.join(dirname, filename)
            
            result = extract_data_from_file(filepath)
            if result==[]:
                print("Error:{}".format(filepath))
                xie='{}'.format(m)
                xiae=np.array(xie)
                yie='{}'.format(n)
                yiae=np.array(yie)
                Xe=np.vstack((Xe,xiae))
                ye=np.vstack((ye,yiae))
            else:
                print("From {}: {}".format(filepath, result))
                xi='{}'.format(m)
                xia=np.array(xi)
                yi='{}'.format(-n)
                yia=np.array(yi)
                zi1=np.array(result[0])
                #zi2=np.array(result[1])
                #zi3=np.array(result[2])
                #zi4=np.array(result[3])
                X=np.vstack((X,xia))
                y=np.vstack((y,yia))
                z1=np.vstack((z1,zi1))
                #zi2=np.vstack((z2,zi2)) 
                #zi3=np.vstack((z3,zi3))
                #zi4=np.vstack((z4,zi4))
    result1 = np.hstack((X, y, z1))
    resulte = np.hstack((Xe, ye))
    df = pd.DataFrame(result1)
    df.columns = ['x', 'y', 'z']
    dfe = pd.DataFrame(resulte)
    #dfe.columns = ['x', 'y']

    # Save DataFrame to Excel file with dynamic filename
    try:
        output_path = get_output_filename(ATOM1, ATOM2, ATOM3, "legacy", "energy")
    except:
        output_path = f"{ATOM1.lower()}_{ATOM2.lower()}_{ATOM3.lower()}_input_force.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Energy data saved to: {output_path}")
    
    # Optional: save error data
    if len(resulte) > 1:  # If there is error data
        try:
            error_path = get_output_filename(ATOM1, ATOM2, ATOM3, "legacy", "errors")
        except:
            error_path = f"{ATOM1.lower()}_{ATOM2.lower()}_{ATOM3.lower()}_errors.xlsx"
        dfe.to_excel(error_path, index=False)
        print(f"Error data saved to: {error_path}")
    
    print(f"Processing completed! Total processed {len(result1)-1} successful files, {len(resulte)-1} failed files")

if __name__ == "__main__":
    main()
