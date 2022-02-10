#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 10:47:01 2020

@author: admin
"""

#=====================================
# Import all met data
# QC and organize into dfs
#=====================================

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
plt.style.use('ggplot')
# data folder
data = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\DATA'
format_data = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\PROJECT\Kennicott-Glacier-Sharing\DATA'

#%%
# -------------------------
# Quick plotting Functions
# -------------------------

def plotRecord(ts,dates,title):
    "quickly plot simple time series of air temp data"
    
    plt.close('all')
    from pandas.plotting import register_matplotlib_converters
    fig, ax1 = plt.subplots(figsize=(12,9))
    ax1.set_title(title, size=20)
    ax1.plot(dates,ts)
    ax1.tick_params(axis='x',labelsize=14)
    ax1.set_ylabel('Air Temperature (C)',size=16)
    plt.grid('on')
    plt.tight_layout()
    plt.show()

def plot3(dates,ts,labels,title):
    
    plt.close('all')

    fig, ax1 = plt.subplots(figsize=(12,9))
    ax1.set_title(title, size=20)
    colors = ['blue','purple','red']
    for s,l,c in zip(ts,labels,colors):
        ax1.plot(dates,s,label=l,color=c)
    
    ax1.tick_params(axis='x',labelsize=14)
    ax1.set_ylabel('Air Temperature (C)',size=16)
    ax1.legend()
    plt.grid('on')
    plt.tight_layout()
    plt.show()

def ftm(value, reverse=False):
    "function to convert between m and ft. Default is ft to m, but can handle reverse"
    
    new_val = value * (12 * 2.54 / 100) # ft to m
    
    if reverse:
        new_val = value * (100 / (12 * 2.54)) #m to ft
        
    return new_val
    
#%%
#-----------
# MAY CREEK
#-----------
# --- Compile station metadata
may_meta = pd.DataFrame(data=[[487.7,61.6028,-142.5844,'USR0000AMAY']],
                          columns=['el','lat','lon','ID']) # el in m
may_path = os.path.join(data,'climatedata/MayCreekRAWS_19900501-20200713.csv')
may_full = pd.read_csv(may_path, header=1,parse_dates={'datetime':[0,1]},
                       index_col='datetime')
# just grab temperature column
may_full = may_full.loc[:,'Air Temperature (F)']
# subset years
may_full.index = pd.to_datetime(may_full.index).tz_localize('Etc/GMT-9').tz_convert('US/Alaska')
may_full.columns = 'T2'
start = pd.Timestamp('2016-01-01 00:00:00',tz='US/Alaska')
end = may_full.index[-1]
mayseries = may_full.loc[start:end] # just temperature series
# replace bad values
mayseries.replace(-9999,np.nan,inplace=True)
# convert to celcius
mayseries = (mayseries - 32) * (5/9)
# resample to daily
may = mayseries.resample('D').agg(['min','mean','max']) 
may.columns = ['TMIN','TAVG','TMAX']

#%%
# ----------
# GATES GL
# ----------
# --- Compile station metadata
gates_meta = pd.DataFrame(data=[[1237.5,61.6028,-143.0131,'USR0000AGAT']],
                          columns=['el','lat','lon','ID']) # el in m
# --- Record 1
# load csv of full record downloaded from NPS IRMA site
#  https://irma.nps.gov/DataStore/Reference/Profile/2266884
gates_path = os.path.join(data, 'climatedata/WC_G_GGLA2.csv')
# contains full record, only take useful cols
#cols = [1,2,3,8,9,20,21] # rain, avgT, sd and quality parameters for each
gates_full = pd.read_csv(gates_path,skip_blank_lines=False,
                         header=14,parse_dates=['timestamp_utc'])
# --- parse down to 2016 - 2019
# convert index to AK time
gates_full.loc[:,'DATE'] = gates_full['timestamp_utc'].dt.tz_localize('utc').dt.tz_convert('US/Alaska')
gates_full = gates_full.set_index(['DATE'])
# subset data into new df 
start = pd.Timestamp('2016-01-01 00:00:00',tz='US/Alaska')
end = gates_full.index[-1]
gates_sub = gates_full.loc[start:end,['atf','sdi']]  # order is date, temp, sd
gates_sub.columns = ['T2','SDI']  # rename for concat         

# ---- Record 2
# load csv of ~last year data from Gates Gl (not finalized)
# accessed via https://download.synopticdata.com/#a/GGLA2
gates2019_path = os.path.join(data,'climatedata/GGLA2.2020-07-07.csv')
# read in
gates2019 = pd.read_csv(gates2019_path, header=10, skiprows=[11],
                        parse_dates=['Date_Time'])
# convert time to AK then coerce to hourly timestamps
gates2019.loc[:,'DATE'] = gates2019['Date_Time'].dt.tz_convert('US/Alaska')
gates2019.loc[:,'DATE'] = gates2019.DATE - pd.Timedelta(33,'minutes') # on the hour
gates2019 = gates2019.set_index(['DATE'])
# subset for concatenation
start2 = end + pd.Timedelta(1,'hour') # don't duplicate values from the QC-ed data in gates_sub
gates2019_sub = gates2019.loc[start2:,['air_temp_set_1','snow_depth_set_1']]
gates2019_sub.columns = ['T2','SDI'] # rename for concat

# --- Concatenate dataframes to combine record
gates = pd.concat([gates_sub,gates2019_sub]) # should be no duplicates but can check
# gates[gates.index.duplicated(keep=False)]
# convert F to C
gates.loc[:,'T2'] = (gates.T2 - 32) * (5/9)

# --- Resample to daily
gatesdd = gates.resample('D')['T2'].agg(['min','mean','max']) # resample by day and grab max, min, and avg
gatesdd.columns = ['TMIN','TAVG','TMAX'] # rename columns

# # --- plot
# ts = [gatesdd.TMIN,gatesdd.TAVG,gatesdd.TMAX]
# labels = ['tmin','tavg','tmax']
# dates = gatesdd.index
# title = 'Gates Glacier Record el {} m'.format(gates_meta.el[0])
# plot3(dates,ts,labels,title)

#%%
#------------
# BURI AWS
#------------
# complile metadata
buri_meta = pd.DataFrame(data=[[606,61.4841,-142.9283]],
                         columns=['el','lat','lon']) # el in m, ll in deg

# txt file of hourly 2-m air temp from Pascal Buri in 2019
buri_path = os.path.join(data,'climatedata/BURI_AWS_2019.txt') # dates in AKDT
      
# --- read with pandas
buri = pd.read_table(buri_path,parse_dates=['Date'])
buri.columns  # view/rename headers
buri.rename({'T_a2m':'T2'},axis='columns',inplace=True) # rename temperature column
# some dates in middle are messed up, so make clean date column
date_index = pd.date_range(start=buri.iloc[0,0],end=buri.iloc[-1,0],
                           freq='H')
buri.index = date_index.tz_localize(tz='US/Alaska') # make new date column the index

# ---- New df with daily tmax,tmin,tavg data
buridd = buri.resample('D')['T2'].agg(['min','mean','max']) # resample by day and grab max, min, and avg
buridd.columns = ['TMIN','TAVG','TMAX'] # rename columns
# ---plot
# ts = [buridd.TMIN,buridd.TAVG,buridd.TMAX]
# dates = buridd.DATE
# labels = ['TMIN','TAVG','TMAX']
# title = 'AWS lower Kennicott at {} m elevation'.format(buri_meta.el[0])
# plot3(dates,ts,labels,title)

#%%
#----------------
# USGS GAGE DATA
#----------------

# ---compile metadata 
# elevation relative to NGVD29, lat/lon reference to NAD27
gage_meta = pd.DataFrame(data=[[408.83,'61.4332895824','-142.9446852347']],
                         columns=['el','lat','lon']) # el in m, NAVD 88
# convert rough el to m
# csv of 15 minute air temperatures (C) from USGS Kenn gage
gage_path = os.path.join(data,'climatedata/USGS_15209700_airtemp.csv')

# --- read in with pandas CAUTION: 122k lines long...very big!
gageraw = pd.read_csv(gage_path,usecols=[1,2],header=14) #, parse_dates=['Timestamp (UTC-09:00)'])
gageraw.columns = ['DATE','Temp']

# --- shorten into TMIN, TAVG, TMAX
gageraw.index = pd.to_datetime(gageraw.DATE)
gage = gageraw.resample('D')['Temp'].agg(['min','mean','max']) # resample by day
gage.columns = ['TMIN','TAVG','TMAX'] # rename 
gage.index = gage.index.tz_localize(tz='US/Alaska')

# # ---plot 
# ts = [gage.TMIN,gage.TAVG,gage.TMAX]
# dates = gage.DATE
# labels = ['TMIN','TAVG','TMAX']
# title = 'USGS GAGE Air Temp'
# plot3(dates,ts,labels,title)

#%%
#--------------------
# NWS COOP McCarthy
#--------------------

# --- compile metadata
coop_meta = pd.DataFrame(data=[[1250,61.4180,-142.9961,505757]],
                         columns = ['el','lat','lon','ID']) # el in ft
# convert el to m
coop_meta.el = ftm(coop_meta.el)
# text file of daily weather obs from McCarthy town
coop_path = os.path.join(data,'climatedata/NWS_coop_505757_csv.txt')

# --- read in with pandas
coop = pd.read_csv(coop_path,header=2,skip_blank_lines=False,
                      parse_dates = ['Date'])

coop.rename({'Date':'DATE',' MaxTemperature':'TMAX',
                        ' MinTemperature':'TMIN',' AvgTemperature':'TAVG'},
                         axis='columns',inplace=True,errors='raise')
# remove 'M', covert dtypes to float
coop = coop.replace({' M':np.nan,' T':np.nan}) # replace flag values with NaN
coop = coop.set_index('DATE').tz_localize('US/Alaska') # set date as index and localize
coop = coop.astype(float,errors='raise')
# convert to C
coop.loc[:,['TMAX','TAVG','TMIN']] = (coop.loc[:,['TMAX','TAVG','TMIN']]-32) * (5/9)
# coop = coop.drop(columns=[' Precipitation',' Snowfall',' SnowDepth')]
# # --- plot
# ts = [coop.TMAX,coop.TAVG,coop.TMIN]
# dates = coop.DATE
# labels = ['TMAX','TAVG','TMIN']
# title = 'NWS Coop station in McCarthy'
# plot3(dates,ts,labels,title)


#%%
#-------------------
# SAVE DATAFRAMES
#-------------------
#---- Combine into one temperature df
combine = [gatesdd,
           may,
           buridd,
           gage,
           coop.drop(columns=[' Precipitation',' Snowfall',' SnowDepth'])]

names = ['gates','may','buri','usgs','coop'] # become keys in the concat df
t = pd.concat(combine,axis=1,keys=names) # put into single df

# ---- combine metadata into one df
metadata = [gates_meta,may_meta,buri_meta,gage_meta,coop_meta]
names = ['gates','may','buri','usgs','coop'] # use same keys to access
meta = pd.concat(metadata,axis=0,keys=names) # df of dataframes

# --- save dataframes using pandas + pickle
# paths
meta_path = os.path.join(format_data,'temperature_meta.pickle')
temp_path = os.path.join(format_data,'daily_temperature_data.pickle')
# pickle
meta.to_pickle(meta_path)
t.to_pickle(temp_path)
# csv
meta.to_csv(os.path.join(format_data,'temperature_meta.csv'))
t.to_csv(os.path.join(format_data,'daily_temperature_data.csv'))


