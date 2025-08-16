import os
import numpy as np
import pandas as pd
import re
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
            filename = "Ne{},H{}/Ne{},H{}.out".format(m,n,m,n)
            result = extract_data_from_file(filename)
            if result==[]:
                print("Error:{}".format(filename))
                xie='{}'.format(m)
                xiae=np.array(xie)
                yie='{}'.format(n)
                yiae=np.array(yie)
                Xe=np.vstack((Xe,xiae))
                ye=np.vstack((ye,yiae))
            else:
                print("From {}: {}".format(filename, result))
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
                #z2=np.vstack((z2,zi2)) 
                #z3=np.vstack((z3,zi3))
                #z4=np.vstack((z4,zi4))
    result1 = np.hstack((X, y, z1))
    resulte = np.hstack((Xe, ye))
    df = pd.DataFrame(result1)
    df.columns = ['x', 'y', 'z']
    dfe = pd.DataFrame(resulte)
    #dfe.columns = ['x', 'y']

    # 将DataFrame保存为Excel文件
    output_path = "input_force.xlsx"
    df.to_excel(output_path, index=False)
    #output_pathe = "/Users/garyx/Documents/wlhxh/outpute.xlsx"
    #dfe.to_excel(output_pathe, index=False)        

if __name__ == "__main__":
    main()
