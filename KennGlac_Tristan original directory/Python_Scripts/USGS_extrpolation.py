# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:57:16 2020

@author: admin
"""

# =====================
# Combine low-elevation
# temp stations into 
# single USGS record
# =====================

# Imports

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from scipy import stats
# set up
pd.plotting.register_matplotlib_converters()
plt.style.use('ggplot')

# data folder
format_data = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\PROJECT\Kennicott-Glacier-Sharing\DATA'

#%%
# --- Load Data
meta = pd.read_pickle(os.path.join(format_data,'temperature_meta.pickle'))
dd = pd.read_pickle(os.path.join(format_data,'daily_temperature_data.pickle'))


#%% Functions
# construct new gap index
def gap_ix(df):
    
    seasons = {'summer': [7,8,9], # May - September
               'winter_gap': [1,2,3,4,5,6,10,11,12]}
    months = {num:sea for sea in seasons.keys()
                            for num in seasons[sea]}
    # name winter according to year which it starts
    sea = pd.Series(df.index.month).map(months)
    # put back into dataframe
    seaidx = pd.Index(sea,name='GAP')
    df = df.set_index(seaidx,append=True)
    
    return df
# plotting function with regression stats & lines
def temp_scat(x,y,title,labels):
    fig,ax = plt.subplots(figsize=(9,9))
    ax.set_title(title)
    # plot data
    ax.scatter(x,y,s=6,color='steelblue')
    # plot 1 to 1 line
    ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k-', lw=2)
    # put r^2 and regression line on plot
    mask = ~np.isnan(x) & ~np.isnan(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask],y[mask])
    r2 = r_value**2
    xo = np.linspace(x.min(),x.max(),)
    Yhat = (slope*xo) + intercept # regression y coords
    ax.plot(xo,Yhat,'--',linewidth=2,color='darkorchid')
    # annotate with r2 and regression equation
    ax.annotate('$r^2$ = {:.2f}'.format(r2),(-40,-25),fontsize=14)
    ax.annotate('y = {0:.2f}(x) + {1:.2f}'.format(slope,intercept),(5,0),fontsize=12)
    # labels
    ax.axis('square')
    ax.set_xlabel(label[0])
    ax.set_ylabel(label[1])
    fig.tight_layout()
    plt.show()
#%%
# ---- Correlate May with USGS for all data

# Simple scatter with 1 to 1 line
x = dd['may','TAVG']
y = dd['usgs','TAVG']
label = ['May Creek','USGS Gage'] # x label, y label
title = 'May and USGS Temperatures'

temp_scat(x,y,title,label)


#%%
# ---------------------
# Regression & Extrap
# ---------------------

# 1. ---- Subset training data
# get bounds of usgs data gap
start = pd.Timestamp('2018-01-01 00:00:00-0800',tz='US/Alaska')
end = pd.Timestamp('2019-08-01 00:00:00-0800',tz='US/Alaska')
idx=pd.IndexSlice
# grab the usgs TAVG series
period = dd.loc[slice(start,end),idx['usgs','TAVG']] # isolate year with the winter gap
gaps = period.loc[pd.isna(period)].index# find nan indices

# subset may creek, usgs data based on gaps range with new index
dd = gap_ix(dd) # put new index in
train = dd.loc[idx[:,'winter_gap'],idx[['usgs','may'],'TAVG']].copy()
# drop gap index, add index of months
train = train.reset_index(level=1,drop=True) # remove gap index
#month_ix = pd.Index(train.index.month,name='MONTH') # create new index
#train = train.set_index(month_ix,append='True') # add new month index in
# drop columns level
train.columns = train.columns.droplevel(1) # remove TAVG labels 

# plot training data relatinoship
x = train['may']
y = train['usgs']
title = ('Wintertime (October - May) Temperatures')
label = ['May Creek','USGS Gage']

temp_scat(x,y,title,label)

#%%
# 2. --- Check statistics plots

# 1. Histogram 
train.plot(kind='hist',bins=20)
# ... normal enough! Better when June is included

# 2. Residuals plot
x = train['may']
y = train['usgs']
mask = ~np.isnan(x) & ~np.isnan(y)
slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask],y[mask])
Yhat = (slope*x) + intercept # regression-precicted y coords
res = y - Yhat #  actual - predicted

# --- Actual/Predicted Plot
fig,ax = plt.subplots(figsize=(9,9))
ax.set_title('Actual/Predicted Plot',fontsize=18)
ax.scatter(y,Yhat)
ax.set_xlabel('Actual Temperatures')
ax.set_ylabel('Predicted Temperatures')
plt.show()

# --- Residuals vs x
fig,ax = plt.subplots(figsize=(9,9))
ax.set_title('Residuals Plot',fontsize=18)
ax.scatter(x,res)
ax.set_ylabel('Residual (Actual - Predicted)')
ax.set_xlabel('May Creek Temperature')
plt.show()

# good enough?

#%%
# 3. Complete usgs record with adjusted may temps
idx = pd.IndexSlice
dtvg = dd.loc[:,idx[['usgs','gates','buri'],'TAVG']].copy() # new df
dtvg = dtvg.reset_index(level=1,drop=True) # remove gap index
dtvg.columns = dtvg.columns.droplevel(1) # remove tavg index
# direct assignment fill values
may_vals = train.loc[idx[gaps[0]:gaps[-1]],'may'].copy()
fill = (may_vals *  slope) + intercept # slope, intercept defined in cell above
# swap in values
dtvg.loc[idx[gaps[0]:gaps[-1]],'usgs'] = fill # direct fill

# --- save dtvg to pickle
dtvg.to_pickle(os.path.join(format_data,'daily_tavg.pickle'))

#%%


