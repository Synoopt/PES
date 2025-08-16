import os 
string1='''%mem=10GB
%nprocs=8
# sp b3lyp/6-311g** Force nosymm scf=(qc)

Title Card Required

1 2
 H                  0.00    0.00    0.00
'''

    
for i in range(0,71):
    for j in range(0,71):
        m=round(0.5+0.05*i,6)
        n=round(-0.5-0.05*j,6)
        stringi=' H             {}     0.00    0.00'.format(n)
        stringj='\n Ne            {}     0.00    0.00\n\n'.format(m)
        string0=string1+stringi+stringj
        os.makedirs('Ne{},H{}'.format(m,n),exist_ok=True)
        filename = "Ne{},H{}/Ne{},H{}.gjf".format(m,n,m,n)
        f=open(filename,'a+') 
        f.truncate(0) 
        f.write(string0) 
        f.close()


