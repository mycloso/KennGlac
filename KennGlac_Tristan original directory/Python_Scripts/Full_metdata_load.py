# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 15:18:00 2020

@author: tamaral
"""


# ========================
# TRIAL: full met var load
# ...input one large df
# ========================

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
plt.style.use('ggplot')
# data folder
data_folder = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\DATA\climatedata'

gitdata = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\PROJECT\Kennicott-Glacier-Sharing\DATA'

# ---- Stations are organized by elevation; highest to lowest
#%%
# -----------
# UPPER CAWS
# -----------
# --- compile metadata
ucaws_meta = pd.DataFrame(data=[[2185, 61.682967, -143.089917]],
                          columns=['el','lat','lon']) # el in m
# raw path
dat_files = [f for f in os.listdir(data_folder) if f.endswith('.dat')]
upperpath = os.path.join(data_folder,dat_files[1])
# read
upper = pd.read_csv(upperpath,header=0,skiprows=[0,2,3],parse_dates=True,
                    index_col='TIMESTAMP')

# change time zone... appears to already be in AK time zone but not dst
upper.index = upper.index.tz_localize('Etc/GMT+9').tz_convert('US/Alaska')
upper.columns # print to view all variables

# --- variables to keep
# DLR: Downward Longwave radiation (W/m2)
# Rn: net radiation (W/m2)
# Air_T_1_5m: air temperature @ 1m height (C)
# Air_RH_1_5m: relative humidity @ 1m height (%)
# RainSnow: precipitation (mm)
# Pressure: (hPa)
# WS_1_5m: wind speed @ 1m height (m/s)
# WD_1_5m: wind direction @ 1m height (degrees)
# Snow_depth: (cm)

# rename and subset upper
keep = ['DLR_Avg','Rn_Avg','Air_T_1_5m_Avg','Air_RH_1_5m_Avg','RainSnow',
        'Pressure_Avg','WS_1_5m','WD_1_5m','Snow_depth_Avg']

nn = ['DLR','SR','TAVG','RH','PRE','P','WS','WD','SD']
dtype_dict = {v:float for v in keep}
name_dict = {v:n for v,n in zip(keep,nn)}
upper = upper.astype(dtype=dtype_dict)
# subset and rename
upper = upper.loc[:,keep]
upper.rename(columns=name_dict,inplace=True)
upper.columns # view new df variables

# resample to daily
upper = upper.resample('D').mean()

# Quality control- visualize all variables
fig,axs = plt.subplots(3,3,figsize=(18,12))
for col,ax in zip(upper.columns,axs.flatten()):
    upper[col].plot(ax=ax,title=col)
    ax.set_xlabel('')
    plt.show
fig.tight_layout()

# station fell onto side...some data are not useful

# -----------------------------------------------
# SAVE individual df
saveto = os.path.join(gitdata,'upperCAWS.pickle')
upper.to_pickle(saveto)
# -----------------------------------------------

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
gates_path = os.path.join(data_folder, 'WC_G_GGLA2.csv')
# read in with pandas
gates_full = pd.read_csv(gates_path,skip_blank_lines=False,header=14,
                         parse_dates=['timestamp_utc'],index_col=['timestamp_utc'])
# --- parse down to 2016 - 2019
gates_full.index = gates_full.index.tz_localize('utc').tz_convert('US/Alaska')
start = pd.Timestamp('2016-01-01 00:00:00',tz='US/Alaska')
end = gates_full.index[-1]
gates_full = gates_full.loc[start:end,:]  

# --- variables and raw units
# rnin: rainfall (in)
# wsm: wind speed (mph)
# wdd: wind direction (degrees)
# atf: air temperature (fahrenheit)
# rhp: relative humidity (%)
# srw: solar radiation (W/m2)
# sdi: snow depth (in)
# ---- quality flags: 31=good, 11=poor, 6=suspect

# variable naming and subsetting
keepvars = ['rnin','wsm','wdd','atf','rhp','srw','sdi']
keep = keepvars + [str(i)+'_quality' for i in keepvars] 
# new names
nn_v = ['RN','WS','WD','TAVG','RH','SR','SD']
nn = nn_v + [str(j)+'_q' for j in nn_v]
dtype_dict = {v:float for v in keep}
name_dict = {v:n for v,n in zip(keep,nn)}
gates_full = gates_full.astype(dtype=dtype_dict)
# subset and rename
gates_full = gates_full.loc[:,keep]
gates_full.rename(columns=name_dict,inplace=True)
gates_full.columns # view new df variables

# ---- Quality check and plotting
     

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
gatesdd.loc[:,'DATE'] = gatesdd.index.copy() # put date column back in
