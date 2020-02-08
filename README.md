# Global Sensitivity Analysis (GSA) in Hydrus-1D

Evaluate the sensitivity analysis in the hydrodynamics processes is essential to understand the influence of the parameters in the Soil Water Content (SWC). This analysis still allows to determine hydrodinamics parameters with major accuracy. In this context, this project evalueted GSA in a robust Hydrus-1D model. For this, was used Sobol Sensitivity Analysis (doi:10.1016/S0378-4754(00)00270-6) presents in SALib library. The objective function used was the NSE coeficient, were was compared the mensured and simulated SWC. 

The data used in this work was provided by the project INCT-ONDACBC (Observatório Nacional da Dinâmica da Água e de Carbono no Bioma Caatinga). The soil moisture was evalueted by TDR sensors in depth of 10, 20, 30, and 40 cm. This tower is located in a seasonal tropical dry forest (Caatinga) in the semi-arid region of Brazil (Serra Talhada - PE) (http://dx.doi.org/10.17190/AMF/1562386).

Localization towers area:
<img src = "https://github.com/ravellys/Soil-Moisture-estimator-with-Machine-Learn/blob/master/localiza%C3%A7%C3%A3o.png">

## Execute the routine:
1. create a project in Hydrus-1D (BRCST_SA_30dias). 
2. crete a .txt with same content that SELECTOR.IN (selectortxt.txt).
3. put this project paste and the executable H1D_calc.exe in local disk C:.
4. create a file with mensured data (SA_30d_Hydrus).
5. Execute the routine (GSA_hydrus.py)

## How the routine works:

### Libraries used

```
from SALib.sample import saltelli
from SALib.analyze import sobol
import time, subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import hydroeval as hyev
```

### time of the days in Hydrus, Hydrus project, and import mensured data

```
ndias=31

pasta = 'C:/BRGST_SA_30dias'

fileDadosMedidos='SA_30d_Hydrus.xlsx'
DadosMEDIDOS = pd.read_excel(fileDadosMedidos, header = 0)
DadosMEDIDOS.head()
Eta = DadosMEDIDOS['ETa_BRGST'].values
Vreal = DadosMEDIDOS['Vol_BRGST'].values
```

### Create problem

Here we will define the range of the parameters:
```
problem = {
    'num_vars': 6,
    'names': ['thr', 'ths', 'alfa','n','Ks','l'],
    'bounds': [[0.001, 0.05],
               [0.2, 0.6],
               [0.001, 1],
               [1.1,3],
               [10, 10000],
               [-1, 1]]
}
```

### Create the samples 

the total simulations is calculed by: n_samples*(2*n_paramters+2)
```
nsamples = 3000
param_values = saltelli.sample(problem,nsamples)
```

### Execute all simulations

Here we will execute the NSE function, and create a Y matrix with alls NSE coefficients.```
```
Y = []
START=time.time()

for i in range(len(param_values)): 
    nse = NSE(param_values[i],pasta,ndias,tempo,Vreal,Eta)
    Y.append(nse)
    print(i,*param_values[i],*Y[i])

Y = np.array(Y)

print('total time', str(time.time()-START))
```

The NSE function performs the following steps:
1. change hydrus project parameters
2. execute hydrus
3. import outputs in file TLEVEL.out
4. calcule NSE coeficient with mensured and simulated data.

```
def NSE(x,pasta,ndias,tempo,Vreal,Eta):
    
    mudaParametros(pasta,x)
    rodar_Hydrus(pasta) 

    DATA = TLEVEL(pasta+'/T_Level.out',ndias)
    if isinstance(DATA, pd.DataFrame):
        Volume = DATA['Volume'].values
        ETa = desCum(DATA['sum(vRoot)'].values + DATA['sum(Evap)'].values)
    
        NSEv = hyev.nse_c2m(Volume,Vreal)
        NSEeta = hyev.nse_c2m(ETa,Eta)
        return [NSEv,NSEeta]        
 
    else:
        return [-1,-1]
```

### finaly, we used the barplot function to make and plot the sensitives indices
```
variaveis = df_Y.columns
for i in variaveis:
    figura,Sensibilidade = barplot(df_Y[i])
    figura.savefig(pasta + '/'+ estação+ i + '.png' ,dpi=300,bbox_inches='tight')
    df_si = pd.DataFrame(Sensibilidade, columns = ['S1','ST'])
    df_Y.to_excel(pasta + '/'+ estação+ i + '.xlsx',index = True,header = True)
````
 Out: 
<img src = "https://github.com/ravellys/Soil-Moisture-estimator-with-Machine-Learn/blob/master/localiza%C3%A7%C3%A3o.png">
<img src = "https://github.com/ravellys/Soil-Moisture-estimator-with-Machine-Learn/blob/master/localiza%C3%A7%C3%A3o.png">
