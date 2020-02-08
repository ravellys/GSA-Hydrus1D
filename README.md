# Global Sensitivity Analysis (GSA) in Hydrus-1D

Evaluate the sensitivity analysis in the hydrodynamics processes is essential to understand the influence of the parameters in the Soil Water Content (SWC). This analysis still allows to determine hydrodinamics parameters with major accuracy. In this context, this project evalueted GSA in a robust Hydrus-1D model. For this, was used Sobol Sensitivity Analysis (doi:10.1016/S0378-4754(00)00270-6) presents in SALib library. The objective function used was the NSE coeficient, were was compared the mensured and simulated SWC. 

The data used in this work was provided by the project INCT-ONDACBC (Observatório Nacional da Dinâmica da Água e de Carbono no Bioma Caatinga). The soil moisture was evalueted by TDR sensors in depth of 10, 20, 30, and 40 cm. This tower is located in a seasonal tropical dry forest (Caatinga) in the semi-arid region of Brazil (Serra Talhada - PE) (http://dx.doi.org/10.17190/AMF/1562386).


## Execute the routine:
1. create a project in Hydrus-1D (BRCST_SA_30dias). 
2. put this project paste and the executable H1D_calc.exe in local disk C:.
3. create a file with mensured data (SA_30d_Hydrus).
4. Execute routine (GSA_hydrus.py)

