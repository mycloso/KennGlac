# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 16:51:45 2020

@author: tamaral
"""

# ====================
# Ingest Precip Data
# ====================

# Imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,csv
# plotting
pd.plotting.register_matplotlib_converters()
plt.style.use('ggplot')

data_folder = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\DATA\climatedata'
#%%
# ---- SNOTEL - Daily (Start of day) values 
snotel_path = os.path.join(data_folder,'SNOTEL_1096_MayCreek.txt')
# read in with pandas
snotel = pd.read_csv(snotel_path,header=56,parse_dates=True,index_col='Date')
# rename cols, units= mm, mm, cm, mm
# columns are:
# 'May Creek (1096) Precipitation Accumulation (mm) Start of Day Values',
# 'May Creek (1096) Precipitation Increment (mm)',
# 'May Creek (1096) Snow Depth (cm) Start of Day Values',
# 'May Creek (1096) Snow Water Equivalent (mm) Start of Day Values'
snotel.columns = ['Precip_acc','Precip_inc','SDS','SWES'] 
# remove suspect data
snotel['SDS'] = snotel['SDS'].where(snotel.SDS < 100)
snotel.to_csv(os.path.join(data_folder,'snotel_precip.csv'))

#%%
# ----- GATES
# NPS IRMA gates QAQC-ed data through 2019
gates_path = os.path.join(data_folder,'WC_G_GGLA2.csv')
# read with pandas
gates_full = pd.read_csv(gates_path,skip_blank_lines=False,header=14,
                    parse_dates=['timestamp_utc'],index_col=['timestamp_utc'])
# subset out precip columns
gates_full.index = gates_full.index.tz_localize('utc').tz_convert('US/Alaska').rename('DATE')
start = pd.Timestamp('2016-01-01 00:00:00-0800',tz='US/Alaska')
end = gates_full.index[-1]
gates_irma = gates_full.loc[slice(start,end),['sdi','rnin']]
gates_irma.columns = ['SDI','RN'] # rename columns to match

# load csv of ~last year data from Gates Gl (not finalized)
# accessed via https://download.synopticdata.com/#a/GGLA2
gates2019_path = os.path.join(data_folder,'GGLA2.2020-07-07.csv')
# read in
gates2019 = pd.read_csv(gates2019_path, header=10, skiprows=[11],
                        parse_dates=['Date_Time'],index_col=['Date_Time'])
# convert time to AK then coerce to hourly timestamps
gates2019.index = (gates2019.index - pd.Timedelta(33,'minutes')).tz_convert('US/ALASKA').rename('DATE') 
# subset for concatenation
start2 = end + pd.Timedelta(1,'hour') # don't duplicate values from the QC-ed data in gates_sub
gates2019_sub = pd.DataFrame(gates2019.loc[start2:,'snow_depth_set_1'])
gates2019_sub.columns = ['SDI'] # rename for concat

# --- Concatenate dataframes to combine record
gates_precip = pd.concat([gates_irma,gates2019_sub]) 
# remove bad values over 100
gates_precip['SDI'] = gates_precip['SDI'].where(gates_precip['SDI'] < 100)

# convert values to metric
gates_precip = gates_precip * 2.54 # convert inches to cm
gates_precip['RN'] = gates_precip.loc[:,'RN'] * 10 # cm to mm
# visualize
gates_precip.SDI.plot()
# ....some gaps in all years, but general snow depth trend intact
gates_precip.RN.plot()
# .... only rain data for first three years

# resample to daily: mean for hourly SD and sum for hourly rain accum.
gatesdd_precip = gates_precip.resample('D').agg({'SDI':'first','RN':'sum'})

#---- plot time series on top
pd.plotting.register_matplotlib_converters()
fig,[ax1,ax2] = plt.subplots(2,1,figsize=(16,9))
#  plot snow
ax1.plot(gatesdd_precip.index,gatesdd_precip.SDI,color='gray')
ax1.set_title('Gates Glacier Snow Depth (cm)')
# plot rain
ax2.plot(gatesdd_precip.index,gatesdd_precip.RN,color='steelblue')
ax2.set_title('Gates Glacier Rain Precip (cm)')

plt.show()

#%%
# ---- Chinese AWS lower on Kennicott ~675 m. Upper is 2185 m but fell down..
# get paths
dat_files = [f for f in os.listdir(data_folder) if f.endswith('.dat')]
lowerpath = os.path.join(data_folder,dat_files[0])
upperpath = os.path.join(data_folder,dat_files[1])
# read in lower chinese station
caws_raw = pd.read_csv(lowerpath,header=0,skiprows=[0,2,3],parse_dates=True,
                    index_col='TIMESTAMP')
# read in metadata header to get units of precip cols
with open(lowerpath,newline='') as f:
    head = [next(f) for x in range(4)]
# look up units for 'RainSnow'
names = head[1].split(',')
units = head[2].split(',')
rsun = units[names.index('"RainSnow"')] # units are mm
    
# explore
caws_raw = caws_raw.astype(dtype={'Snow_depth_Avg':float})
# resample to daily to match other precip records
caws = caws_raw.resample('D').agg({'Snow_depth_Avg':'mean','RainSnow':'max'})  
caws = caws.loc[:,['Snow_depth_Avg','RainSnow']] # just get precip
caws.columns = ['SD','RS'] # rename
# coerce closer to actual values
corr = 176.4 # cm; correction height for snow depth sensor
caws['SD'] = caws['SD'] + corr # try to get non-snow values back near 0
# make new precip inc column
caws['Precip_inc'] = caws.RS.diff() # find row differences
caws.Precip_inc.loc[caws.Precip_inc < 0] = np.nan


# plot side by side
fig,[ax1,ax2]= plt.subplots(1,2,figsize=(16,8))
caws.RS.plot(ax=ax1,title='Accumulated Precip')
ax1.set_ylabel('mm'),ax1.set_xlabel('')
caws.SD.plot(ax=ax2,title='Snow Depth')
ax2.set_ylabel('cm'),ax2.set_xlabel('')
plt.show()


#%%

# ---- Plot suitable precip data (non-snow) on one plot
# gates and SNOTEL
fig,[ax1,ax2,ax3,ax4] = plt.subplots(4,1,sharex=True,figsize=(12,8))
g,s = 'steelblue','darksalmon'
# precip plots
ax1.set_title('Gates Rainfall')
ax1.plot(gates_precip.index,gates_precip.RN,label='Gates',color=g)
ax1.set_ylabel('mm')
ax1.legend()
ax2.set_title('SNOTEL Rainfall')
ax2.plot(snotel.index,snotel.Precip_inc,label='SNOTEL',color=s)
ax2.set_ylabel('mm')
ax2.legend()

# snowfall
ax3.set_title('Gates Snowfall')
ax3.plot(gates_precip.index,gates_precip.SDI,label='Gates',color=g)
ax3.set_ylabel('cm snow')
ax3.legend()
ax4.set_title('SNOTEL Snowfall')
ax4.plot(snotel.index,snotel.SDS,label='SNOTEL',color=s)
ax4.set_ylabel('cm snow')
ax4.legend()

fig.tight_layout()
plt.show()

#%% 
# --- correlate precip records
































# --- Concatenate into precip record


