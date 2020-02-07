
"""
CÁLCULO DA SENSIBILIDADE GLOBAL PELO MÉTODO SOBOL(2001)
LUCAS RAVELLYS - UFPE- DEN - GRUPO DE FÍSICA DO SOLO
"""


# IMPORTAR BIBLIOTECAS
from SALib.sample import saltelli
from SALib.analyze import sobol
import time, subprocess
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import hydroeval as hyev
import seaborn as sns


# FUNÇÕES UTILIZADAS MUDAR PARAMETROS HIDRODINAMICOS DO MODELO DE POROSIDADE ÚNICA DE VAN GENUTCHEN MUALEN NO HYDRUS-1D
def mudaParametros (pasta,vg):
    
    file = pasta + '/selectortxt.txt'
    fileout = pasta +'/SELECTOR.IN'
    
    cont = 1
    fr = open(file,'r')
    fw = open(fileout,'w')
 
    for line in fr.readlines():
        if cont == 27: #Position of VGM parameters
            fw.writelines('  %f    %f   %f   %f    %f     %f \n' %(vg[0], vg[1], vg[2], vg[3], vg[4], vg[5]))
        else:
            fw.writelines(line)
        cont=cont+1
    fr.close()
    fw.close()

# EXECUTA O HYDRUS
def rodar_Hydrus(pasta,tempo):
    guessed_runtime = tempo
    ps = subprocess.Popen(['C:/H1D_CALC.exe',pasta],  stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, shell = True,close_fds=True)
    ps.communicate()
    ps.terminate()
        

# LÊ A SAIDA DO HYDRUS COMO DATAFRAME
def Floats (ARRAY):
    return [float(x) for x in ARRAY.split()]

def TLEVEL (file, ndias):    
    obsnode = pd.read_csv(file, skiprows = 7,sep='\t')
    obsnode.head()

    Obsnode = obsnode.values
    
    if Obsnode[len(Obsnode)-1]=='end':
        
        nlin = len(Obsnode) - 2

        floats = [float(x) for x in Obsnode[0,0].split()]
        ncolum = len(floats)

        ObsnodeFloat = np.zeros((ndias,ncolum)) 

        j=0
        antfloat = -1
        for i in range(nlin) :    
            FLOATS = Floats(Obsnode[i+1,0])
            if FLOATS[0]%1 == 0 and FLOATS[0] != antfloat and FLOATS[0]!=0.0 :
                antfloat = FLOATS[0]
                ObsnodeFloat[j,:] = FLOATS
                j=j+1

        HEAD = 'Time          rTop        rRoot        vTop         vRoot        vBot       sum(rTop)   sum(rRoot)    sum(vTop)   sum(vRoot)    sum(vBot)      hTop         hRoot        hBot        RunOff    sum(RunOff)     Volume     sum(Infil)    sum(Evap) TLevel Cum(WTrans)  SnowLayer'

        DATA = pd.DataFrame(ObsnodeFloat, columns = HEAD.split())
       
        return DATA
    else:
        return -1

def desCum (X): 
    x =  np.zeros(len(X))
    x[0] = X[0]
    for i in range(len(X)-1):
        x[i+1] = X[i+1] - X[i]
    return x

#CALCULA O COEFICIENTE NSE PARA O VOLUME ARMAZENADO E A ETA
def NSE(x,pasta,ndias,tempo,Vreal,Eta):
    
    mudaParametros(pasta,x)
    rodar_Hydrus(pasta,tempo) 

    DATA = TLEVEL(pasta+'/T_Level.out',ndias)
    if isinstance(DATA, pd.DataFrame):
        Volume = DATA['Volume'].values
        ETa = desCum(DATA['sum(vRoot)'].values + DATA['sum(Evap)'].values)
    
        NSEv = hyev.nse_c2m(Volume,Vreal)
        NSEeta = hyev.nse_c2m(ETa,Eta)
        return [NSEv,NSEeta]        
 
    else:
        return [-1,-1]


#EFETUA A ANALISE DE SENSIBILIDADE E PLOTA OS GRAFICOS DE BARRA
def barplot(df):
    fig = plt.figure(figsize = (5,5))
    y=df.values

    Si = sobol.analyze(problem,y)

    x=[r'$\theta\ _{r}$', r'$\theta\ _{s}$', r'$\alpha\ $','n','Ks','l']
    X = np.arange(len(Si['S1']))

    plt.bar(X + 0.00, Si['S1'],color = 'b', width = 0.25, label = r'$S_1$')
    plt.bar(X + 0.25, Si['ST'],color = 'gray', width = 0.25, label = r'$S_T$')
    plt.xticks(X+0.125,(x),fontsize = 14)
    plt.yticks(fontsize = 14)
    plt.title(df.name,fontsize = 14, family = 'serif') 
    plt.legend()
    
    return [fig,Si]

#TEMPO DA SIMULAÇÃO
ndias=31
tempo = 5

#ARQUIVOS UTILIZADOS
pasta = 'C:/BRCST_SA_30dias'
estação ='BRCST_SA_30dias'

fileDadosMedidos='SA_30d_Hydrus.xlsx'
DadosMEDIDOS = pd.read_excel(fileDadosMedidos, header = 0)
DadosMEDIDOS.head()
Eta = DadosMEDIDOS['ETa_BRCST'].values
Vreal = DadosMEDIDOS['Vol_BRCST'].values

#DEFINIÇÃO DO PROBLEMA
problem = {
    'num_vars': 6,
    'names': ['thr', 'ths', 'alfa','n','Ks','l'],
    'bounds': [[0.01, 0.05],
               [0.2, 0.6],
               [0.001, 0.1],
               [1.1, 2.2],
               [10, 1000],
               [0.25, 0.75]]
}

param_values = saltelli.sample(problem,100)

Y = []
START=time.time()

for i in range(len(param_values)): 
    nse = NSE(param_values[i],pasta,ndias,tempo,Vreal,Eta)
    Y.append(nse)
    print(i,*param_values[i],*Y[i])

Y = np.array(Y)

print('total time', str(time.time()-START))

# Salvando dados
df_Y = pd.DataFrame(Y, columns = ['Volume','ETa'])
df_Y.to_excel("NSE.xlxs",index = True,header = True)

df_par = pd.DataFrame(param_values, columns = [r'$\theta\ _{r}$', r'$\theta\ _{s}$', r'$\alpha\ $','n','Ks','l'])
df_par.to_excel("par.xlxs",index = True,header = True)

#realiza analise sensibilidade e plota figuras
variaveis = df_Y.columns
for i in variaveis:
    figura,Sensibilidade = barplot(df_Y[i])
    figura.savefig('GSA'+i+'.png' ,dpi=300,bbox_inches='tight')
    df_si = pd.DataFrame(Sensibilidade, columns = ['S1','ST'])
    df_si.to_excel("GSA" + i + '.xlsx',index = True,header = True)



