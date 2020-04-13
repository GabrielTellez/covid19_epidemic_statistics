import datapackage
import pandas as pd
from io import StringIO
import requests
import numpy as np
import matplotlib.pyplot as plt
import datetime

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
    'Italy': '2020-03-10'
}

def getdata(data_url = 'https://datahub.io/core/covid-19/datapackage.json', resourcename='countries-aggregated_csv'):
    """
    Get data from the web
    data_url : string with url of the data from datahub
    resourcename : resource to use
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

defaultcountrylist=('Colombia', 'Italy', 'US')
d=getdata()
def builddatalist(indicator = 'Confirmed', minindicator=1, countrylist=defaultcountrylist, fulldata=d):
    """
    Build a list of data for selected countries 
    
    Parameters
    ----------
    indicator : indicator to shift the time series
    minindicator : value to start the time series. 
        Day 0 corresponds to the day when indicator >= minindicator
    countrylist : list of countries to build the datalist
    fulldata : raw data for all countries
    """
    datalist={}
    for country in countrylist:
        dat=fulldata[fulldata['Country']==country]
        dat=dat[dat[indicator]>=minindicator]
        dat['Day']=np.arange(len(dat))
        datalist[country]=dat
    return datalist

def plotdata(indicator = 'Confirmed', minindicator=1, show = None, dayrange = {'min': 0, 'max' : -1}, 
             logscale=True, countrylist=defaultcountrylist, fulldata=d):
    """
    Plots data for selected countries and indicator
    
    Parameters
    ----------
    indicator : indicator to shift the time series
    minindicator : value to start the time series. 
        Day 0 corresponds to the day when indicator >= minindicator
    show = column to show on plot. Default = indicator
    dayrange : dict with min, max range to plot. max=-1 is plot all
    logscale: plot in logscale (True) or linear (False)
    countrylist : list of countries to build the datalist
    fulldata : raw data for all countries
    """
    if show is None:
        show=indicator
    datalist=builddatalist(indicator, minindicator, countrylist, d)
    fig, ax = plt.subplots(figsize=(12,6))
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
        df.plot(x='Day',y=show,logy=logscale,label='%s day 0: %s' % (country,dayzero_date),ax=ax, color=color)
        # get quarantine day info
        try:
            quarantine_date=quarantine[country]
        except KeyError:
            print('%s not in quarantine'%(country))
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
    ax.set_ylabel(show)
    ax.set_xlabel('Days from first day when "'+indicator+'" >='+str(minindicator))
    if logscale:
        labellog = ' (log scale)'
    else:
        labellog = ''   
    ax.set_title(show+' covid-19' + labellog)
    ax.grid()
    ax.legend()
    return fig

