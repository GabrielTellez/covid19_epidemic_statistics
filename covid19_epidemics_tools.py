import datapackage
import pandas as pd
from io import StringIO
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})


# Quarantine start date
# Data from
# https://www.businessinsider.com/countries-on-lockdown-coronavirus-italy-2020-3

quarantine = {
    'United Kingdom': '2020-03-23',
    'Hungary': '2020-03-28',
    'Singapore': '2020-04-07',
    'United Arab Emirates': '2020-03-26',
    'Russia': '2020-03-20',
    'South Africa': '2020-03-26',
    'New Zealand': '2020-03-25',
    'Saudi Arabia': '2020-03-25',
    'Colombia': '2020-03-24',
    'India': '2020-03-24',
    'Australia': '2020-03-31',
    'China': '2020-01-23',
    'Jordan': '2020-03-21',
    'Argentina': '2020-03-21',
    'Israel': '2020-03-25',
    'Belgium': '2020-03-17',
    'Germany': '2020-03-20',
    'Malaysia': '2020-03-16',
    'Czech Republic': '2020-03-16',
    'France': '2020-03-16',
    'Morocco': '2020-03-15',
    'Kenya': '2020-03-15',
    'Spain': '2020-03-14',
    'Poland': '2020-03-13',
    'Kuwait': '2020-03-13',
    'Ireland': '2020-03-27',
    'Norway': '2020-03-12',
    'El Salvador': '2020-03-11',
    'Denmark': '2020-03-13',
    'Italy': '2020-03-10',
    'US': '2020-03-23',
    'Venezuela': '2020-03-17'
}

def getdata(data_url = 'https://datahub.io/core/covid-19/datapackage.json', resourcename='countries-aggregated_csv'):
    """
    Get data from the web.

    Parameters:
    ===========

    data_url : string with url of the data from datahub
    
    resourcename : resource to use

    Output:
    =======

    pd.DataFrame with the epidemic statistics data

    """

    # to load Data Package into storage
    package = datapackage.Package(data_url)
    resources = package.resources

    for resource in resources:
        if resource.name == resourcename:
            url=resource.descriptor['path']
            print('Importing',url)
            s=requests.get(url).text
            data = pd.read_csv(StringIO(s))
    return data

def readdata(filenamebase='data/covid_data_',date=datetime.date.today().isoformat()):
    """
    Reads the data from CSV file
    
    Parameters:
    
    filenamebase : basename of the saved file. Full filename is filenamebase + date + '.csv'
    date : date of the data. Default: today's date 
    
    Output:
    
    pd.DataFrame
    
    """
    filename='%s%s.csv' % (filenamebase,date)
    with open(filename,'r') as file:
        data=pd.read_csv(file)
    return data

def savedata(dataframe,filenamebase='data/covid_data_',date=datetime.date.today().isoformat()):
    """
    Save the dataframe as CSV file
    
    Parameters
    ----------

    dataframe : pd.DataFrame to save. Default 'covid_data_'
    
    filenamebase : basename of the saved file. Full filename is filenamebase + date + '.csv'
    
    date : date of the data. Default: today's date
    """
    filename='%s%s.csv' % (filenamebase,date)
    with open(filename,'w') as file:
        dataframe.to_csv(file,index=False)

defaultcountrylist=['Colombia', 'Italy', 'US']
d=getdata()
typeshow_options = {
    'cumulative' : None,
    'daily increase' : 'diff',
    'daily percentage increase' : 'pct_change'
} 
def builddatalist(indicator = 'Confirmed', minindicator=1, show = None, showtype='cumulative', countrylist=defaultcountrylist, 
    fulldata=d , wpfile='data/world_population_2020.csv'):
    """
    Build a list of data for selected countries 
    
    Parameters
    ----------
    indicator : indicator to shift the time series. Posible values: 
        'Date, 
        'Confirmed', 'Recovered', 'Deaths', 'Infected', 
        'Confirmed/Total Population', 'Recovered/Total Population', 
        'Deaths/Total Population', 'Infected/Total Population',
        'Recovered/Confirmed', 'Deaths/Confirmed', 'Infected/Confirmed
    
    minindicator : value to start the time series. 
        Day 0 corresponds to the day when indicator >= minindicator
    
    show : column to show. Default = indicator. Posible values:
        'Confirmed', 'Recovered', 'Deaths', 'Infected', 
        'Confirmed/Total Population', 'Recovered/Total Population', 
        'Deaths/Total Population', 'Infected/Total Population',
        'Recovered/Confirmed', 'Deaths/Confirmed', 'Infected/Confirmed
    
    showtype : 'Cumulative' (default) no change in column 'show'. 
        Other options: 'Daily increase', 'Daily percentage increase'. These are created on demand.
    
    countrylist : list of countries to build the datalist
    
    fulldata : raw data for all countries  

    wpfile : filename of the world population data
    """
    if show is None:
        show=indicator
    indicator_list = ['Confirmed', 'Recovered', 'Deaths', 'Infected']
    wp=pd.read_csv(wpfile, sep=';', index_col='Country' )
    pop=wp.T.to_dict()
    datalist={}
    for country in countrylist:
        dat=fulldata[fulldata['Country']==country].copy()
        dat['Infected']=dat['Confirmed']-dat['Recovered']-dat['Deaths']
        popul=pop[country]['Population 2020']
        for col in indicator_list:
            if col != 'Confirmed':
                name='%s/Confirmed' % (col)
                dat[name]=dat[col]/dat['Confirmed']
            name='%s/Total Population' % (col)
            dat[name]=dat[col]/(popul*1000)
        dat=dat[dat[indicator]>=minindicator]
        # Check and create increase column if necessary
        preprocess_method=typeshow_options.get(showtype, None)
        if preprocess_method is not None:
            # this method creates the new column: dat[indicator].diff() or pct_change()
            method = getattr(dat[show],preprocess_method)
            label = '%s %s' % (show, showtype)
            dat[label]=method()
        dat['Day']=np.arange(len(dat))
        datalist[country]=dat
    return datalist

def plotdata(indicator = 'Confirmed', minindicator=1, show = None, showtype='cumulative', dayrange = {'min': 0, 'max' : -1}, 
             logscale=True, countrylist=defaultcountrylist, fulldata=d, figsize=(9.5,5), wpfile='data/world_population_2020.csv'):
    """
    Plots data for selected countries and indicator
    
    Parameters
    ----------
    
    indicator : indicator to shift the time series. Posible values: 
        'Date, 
        'Confirmed', 'Recovered', 'Deaths', 'Infected', 
        'Confirmed/Total Population', 'Recovered/Total Population', 
        'Deaths/Total Population', 'Infected/Total Population',
        'Recovered/Confirmed', 'Deaths/Confirmed', 'Infected/Confirmed
    
    minindicator : value to start the time series. 
        Day 0 corresponds to the day when indicator >= minindicator
    
    show : column to show. Default = indicator. Posible values:
        'Confirmed', 'Recovered', 'Deaths', 'Infected', 
        'Confirmed/Total Population', 'Recovered/Total Population', 
        'Deaths/Total Population', 'Infected/Total Population',
        'Recovered/Confirmed', 'Deaths/Confirmed', 'Infected/Confirmed    
    
    dayrange : dict with min, max range to plot. max=-1 is plot all
    
    logscale: plot in logscale (True) or linear (False)
    
    countrylist : list of countries to build the datalist
    
    fulldata : raw data for all countries

    figsize : figure size (to be passed to plt.subplot)

    wpfile : filename of the world population data
    """
    if show is None:
        show=indicator
    datalist=builddatalist(indicator, minindicator, show, showtype, countrylist, d, wpfile)
    fig, ax = plt.subplots(figsize=figsize)
    if showtype == 'cumulative':
        ylabel = show
    else:
        ylabel = '%s %s' % (show, showtype)
    
    for country in countrylist:
        color = next(ax._get_lines.prop_cycler)['color']
        df=datalist[country]
        if df.empty:
            continue
        df=df[dayrange['min'] <= df['Day']]
        if dayrange['max']!=-1 :
            df=df[df['Day']<=dayrange['max']]
        # Get day 0 date
        dayzero_df=df[df['Day']==0]
        dayzero_date=dayzero_df.at[dayzero_df.index[-1],'Date']
        if not isinstance(logscale, bool):
            logscale=True
        df.plot(x='Day',y=ylabel,logy=logscale,label='%s day 0: %s' % (country,dayzero_date),ax=ax, color=color)
        # get quarantine day info
        try:
            quarantine_date=quarantine[country]
        except KeyError:
            print('%s not in quarantine list'%(country))
        else:
            quarantine_day_df=df[df['Date']==quarantine_date]
           #     print(quarantine_day_df)
            try:
                quarantine_day=quarantine_day_df.at[quarantine_day_df.index[-1],'Day']
           #    print(quarantine_day)
            except IndexError:
                # Quarantine date is out of bounds
                print('%s quarantine date %s out of bounds. Day zero is %s' %(country,quarantine_date, dayzero_date))
            else:
                ax.axvline(x=quarantine_day, color=color,
                           label='%s quarantine on day %d (%s)' % (country,quarantine_day,quarantine_date))
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Days from first day when "'+indicator+'" >='+str(minindicator))
    if logscale:
        labellog = ' (log scale)'
    else:
        labellog = ''   
    ax.set_title('%s covid-19 on %s %s' % ( ylabel, datetime.date.today().strftime("%d/%m/%Y"), labellog) )
    ax.grid()
    ax.legend()
    return fig

