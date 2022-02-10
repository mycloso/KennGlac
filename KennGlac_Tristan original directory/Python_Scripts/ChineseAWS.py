# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 14:22:21 2020

@author: tamaral
"""


# ==================
# Ingest Chinese AWS
# 
# Then inspect
# ==================

# Imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

format_data = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\PROJECT\Kennicott-Glacier-Sharing\DATA'
data_folder = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\DATA\climatedata'
#%%
# --- load
# get paths
dat_files = [f for f in os.listdir(data_folder) if f.endswith('.dat')]
lowerpath = os.path.join(data_folder,dat_files[0])
upperpath = os.path.join(data_folder,dat_files[1])
# read
lower = pd.read_csv(lowerpath,header=0,skiprows=[0,2,3],parse_dates=True,
                    index_col='TIMESTAMP')
upper = pd.read_csv(upperpath,header=0,skiprows=[0,2,3],parse_dates=True,
                    index_col='TIMESTAMP')

# change dtype
lower = lower.astype(dtype={'Snow_depth_Avg':float})
upper = upper.astype(dtype={'Snow_depth_Avg':float})

# change time zone... appears to already be in AK time zone but not dst
upper.index = upper.index.tz_localize('Etc/GMT+9').tz_convert('US/Alaska')
lower.index = lower.index.tz_localize('Etc/GMT+9').tz_convert('US/Alaska')

# Rename columns and subset lower
var = ['PTemp','Air_T_3m_Avg','Air_T_1m_Avg','TargTempC_Avg','WS_3m','WS_1m',
       'Snow_depth_Avg']
nn = ['PTemp','TAVG1','TAVG3','Targ','WS3','WS1','SD']
dtype_dict = {v:float for v in var}
name_dict = {v:n for v,n in zip(var,nn)}
lower = lower.astype(dtype=dtype_dict)
# subset & rename for ease
lower = lower.loc[:,var]
lower.rename(columns=name_dict,inplace=True)

# rename and subset upper
var = ['PTemp','Air_T_3m_Avg','Air_T_1_5m_Avg','WS_3m','WS_1_5m',
       'Snow_depth_Avg']
nn = ['PTemp','TAVG3','TAVG1','WS3','WS1','SD']
dtype_dict = {v:float for v in var}
name_dict = {v:n for v,n in zip(var,nn)}
upper = upper.astype(dtype=dtype_dict)
# rename for ease
upper = upper.loc[:,var]
upper.rename(columns=name_dict,inplace=True)

# --- format for saving
lower = lower.resample('D').mean()
upper = upper.resample('D').mean()
# concatenate and pickle for use elsewhere
combine = [lower,upper]
c = pd.concat(combine,axis=1,keys=['lower','upper'])
saveto = os.path.join(format_data,'caws.pickle')
c.to_pickle(saveto)

#%%
# --- Visualize Lower Station
# plot temperatures
fig,axs = plt.subplots(1,4,figsize=(20,6))
for t,ax in zip(nn[:4],axs.flatten()): # just temp variables
    ax.plot(lower.index,lower[t])
    ax.set_title(t,fontsize=18)
fig.tight_layout()
plt.show()

# plot some differences
fig,ax = plt.subplots()
ax.plot(lower.index,(lower.TAVG3 - lower.TAVG1))
ax.set_title('T3 - T1 Temperatures')
plt.show()

fig,ax = plt.subplots()
ax.plot(lower.index,(lower.PTemp - lower.TAVG1))
ax.set_title('PTemp - T1 Temperatures')
plt.show()


# examine snow depth
fig,ax = plt.subplots()
ax.plot(lower.index,lower.SD)
ax.set_title('Snow depth (cm)')
plt.show()

# try to normalize to baseline values
med = np.nanmedian(lower.SD)

# resample to daily 
lowerdd = lower.resample('D').mean()
# gives reasonable time series of snow depths
fig,ax = plt.subplots()
ax.plot(lowerdd.index,(lowerdd.SD - med))
ax.set_title('Snow depth (cm)')
plt.show()

#%%

# --- explore and visualize upper station 

# look at relevant variables
fig,axs = plt.subplots(1,3,figsize=(20,6))
for t,ax in zip(nn[:3],axs.flatten()): # just temp variables
    ax.plot(upper.index,upper[t])
    ax.set_title(t,fontsize=18)
fig.tight_layout()
plt.show()

# examine snow depth
fig,ax = plt.subplots()
ax.plot(upper.index,upper.SD)
ax.set_title('Snow depth (cm)')
plt.show()
# snow depth data look useless

# examine wind speed
fig,ax = plt.subplots()
ax.plot(upper.index,upper.WS1)
plt.show()

#%%

