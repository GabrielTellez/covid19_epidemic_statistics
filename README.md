# covid19_epidemic_statistics
Visualization and analysis of COVID-19 epidemic data statistics

## Files:

### [covid19_epidemics_tools.py](covid19_epidemics_tools.py) 
Module with function utilities to get and visualize data. Plots data for several countries to compare them.

### [testing.ipynb](testing.ipynb)
Jupyter Python example notebook using the tools from covid19_epidemics_tools.py and the matplotlib library.

### [testing_plotly.ipynb](testing.ipynb)
Jupyter Python example notebook using the tools from covid19_epidemics_tools.py and the plotly library.

### [2020_04_28.ipynb](2020_04_28.ipynb)
Jupyter Python notebook with plots of some indicators on 2020/04/28.

### [tmp/](tmp)
Scratch area for new code test

### [plots/](plots)
Some plots obtained with the code.

### [data/](data)
Backups of epidemic statistic data. Up to date data is from  
https://datahub.io/core/covid-19/datapackage.json  
based from Johns Hopkins University Center for Systems Science and Engineering (CSSE) data at:  
https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6


## Dependencies:
Install dependencies using conda:  
covid_env.yml YML file to recreate conda environment:  
conda env create -f covid_env.yml  

or

using pip:  
pip install -r requirements.txt



