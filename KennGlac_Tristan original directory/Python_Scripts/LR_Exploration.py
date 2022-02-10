#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 13:39:40 2020

@author: admin
"""

# ====================
# Do initial LR 
# exploration
# ====================

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from scipy import stats
import matplotlib.dates as mdates
# set up
pd.plotting.register_matplotlib_converters()
plt.style.use('ggplot')

# data folder
format_data = r'C:\Users\tamaral\Documents\GIP-2020\Kennicott\PROJECT\Kennicott-Glacier-Sharing\DATA'

#%%
# --- Load dataframes
dtvg = pd.read_pickle(os.path.join(format_data,'daily_tavg.pickle'))
meta = pd.read_pickle(os.path.join(format_data,'temperature_meta.pickle'))

#%%
# ---- calculate lapse rates for summer

def lr_ix(df):
    
    seasons = {'melt': [4,5,6,7,8,9,10], # April - November
               'non-melt': [1,2,3,11,12]}
    months = {num:sea for sea in seasons.keys()
                            for num in seasons[sea]}
    # name winter according to year which it starts
    sea = pd.Series(df.index.month).map(months)
    # put back into dataframe
    seaidx = pd.Index(sea,name='MELT')
    df = df.set_index(seaidx,append=True)
    
    return df

def lr_plot(daily,freq, drop_buri=True,plot=True):
    """ daily is the daily dataframe, freq is the frequency period to
    resample over. Also returns melt dataframe."""
    
    if freq != 'D':
        # resample
        df = daily.resample(freq).mean()
    else:
        df = daily.copy()
    # add melt season index in
    df = lr_ix(df)
    # subset just melt season out, drop index
    idx = pd.IndexSlice
    melt = df.copy()
    melt.loc[idx[:,'non-melt'],:] = np.nan # turn non-melt values to nan
    if drop_buri:
        melt = melt.drop(['buri'],axis=1) # drop buri for now
    
    melt = melt.reset_index(level=1,drop=True) # drop melt index
    # calculate lapse rate (high minus low) C per km
    melt['lapse'] = 1000 * (melt['gates'] - melt['usgs']) / (meta.el['gates'][0] - meta.el['usgs'][0])
    
    if plot:# plot
        plt.close()
        melt.lapse.plot()
    
    return melt

#%%
# resample to 3d and weeks then visualize
for f  in ['3D','W','2W','M']
    melt = lr_plot(dtvg,f)

# 1. --- Correspondence with temperatures
# daily 
melt = lr_plot(dtvg,'D',plot=False)

# temps subplots
fig,[ax1,ax2] = plt.subplots(1,2,figsize=(15,8))
# usgs
ax1.scatter(melt['usgs'],melt['lapse'],color='steelblue',s=20)
ax1.set_title('USGS Temp Record, {}m'.format(meta.el['usgs'][0]),fontsize=18)
ax1.set_ylabel('Lapse Rate (C/km)',fontsize=14)
ax1.set_xlabel('USGS TAVG',fontsize=14)
# gates
ax2.scatter(melt['gates'],melt['lapse'],color='darkorchid',s=20)
ax2.set_title('Gates Temp Record, {}m'.format(meta.el['gates'][0]),fontsize=18)
ax2.set_ylabel('Lapse Rate (C/km)',fontsize=14)
ax2.set_xlabel('Gates TAVG',fontsize=14)
fig.tight_layout()
plt.show()

# --- regress LR with just gates temps
above = pd.DataFrame(data={'gates': melt['gates'].loc[melt['gates']>= 0],
                           'lapse': melt['lapse'].loc[melt['gates']>= 0]})
# plot up
fig,ax = plt.subplots(figsize=(10,8))
# data points
x,y = above['gates'],above['lapse']
ax.scatter(x,y,color='darkorchid',s=20)
ax.scatter(melt['gates'].loc[melt['gates']< 0], melt['lapse'].loc[melt['gates'] < 0],
           color='darkorchid',s=20, alpha=0.3)
# regression
mask = ~np.isnan(x) & ~np.isnan(y)
slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask],y[mask])
r2 = r_value**2
xo = np.linspace(x.min(),x.max(),)
Yhat = (slope*xo) + intercept # regression y coords
ax.plot(xo,Yhat,'-',linewidth=4,color='k')
# annotate with r2 and regression equation
ax.annotate('$r^2$ = {:.2f}'.format(r2),(15,-5),fontsize=14)
ax.annotate('y = {0:.2f}(x) - {1:.2f}'.format(slope,-intercept),(15,5),fontsize=12)
# labels
ax.set_title('Daily TAVG Lapse Rates')
ax.set_ylabel('Lapse Rate (C/km)',fontsize=14)
ax.set_xlabel('Gates TAVG',fontsize=14)
fig.tight_layout()
plt.show()

# examine histogram of lapse rates
plt.figure()
above['lapse'].plot(kind='hist',bins=15)
# ,... look okay
above['gates'].plot(kind='hist')

# boxplot
plt.figure(figsize=(8,8))
above['lapse'].plot(kind='box',title='Median Value = {0:.2f} (C/km)'.format(np.nanmedian(above['lapse'])))
plt.show()


# Next, look at actual vs predicted
Yxhat = (slope*x) + intercept # regression-precicted y coords
res = y - Yxhat #  actual - predicted

# --- Actual/Predicted Plot
fig,ax = plt.subplots(figsize=(9,9))
ax.set_title('Actual/Predicted Plot',fontsize=18)
ax.scatter(y,Yxhat)
ax.set_xlabel('Actual Lapse Rate')
ax.set_ylabel('Predicted Lapse Rate')
plt.show()

# --- Residuals Plot
fig,ax = plt.subplots(figsize=(9,9))
ax.set_title('Residuals Plot',fontsize=18)
ax.scatter(x,res,color='steelblue')
ax.set_ylabel('Residuals (Actual - Predicted)',fontsize=14)
ax.set_xlabel('Gates Daily TAVG',fontsize=14)
plt.show()



# boxplots
plt.figure()
melt.lapse.plot(kind='box') 

# boxplot by summer season
years = [2016,2017,2018,2019,2020]
data = []
fig,ax = plt.subplots(figsize=(8,8))
ax.set_title('Weekly lapse rates by year',fontsize=16)
# put data into list for plotting
for year in years:
    # remove nan rows
    melt = melt.dropna(subset=['lapse'])
    cut = melt[melt.index.year == year]['lapse']
    data.append(np.array(cut)) # just keep lapse values, not index
   
ax.boxplot(data)
ax.set_xticklabels(str(y) for y in years)
plt.show() 
    
   



















#%%
# --- Slice out summer period... ONLY NECESSARY ONCE, NOW OBSOLETE CODE

# visually select lapse rate summer season (above inflection pt)
fall,spring,n = [],[],0
while n < 2:
    # use mouse clicks on plot (do 2x?)
    fig,ax = plt.subplots(figsize=(14,8))
    ax.plot(tw.index,tw.usgs,linewidth=3,label='usgs')
    ax.plot(tw.index,tw.gates,linewidth=3,label='gates')
    ax.legend()
    
    # store mouse clicks, click 8 times
    coords = plt.ginput(n=8,timeout=120)
    plt.tight_layout()
    plt.show()
    plt.close()
    # convert to date
    coords = mdates.num2date(np.array(coords)[:,0])
    coords = pd.to_datetime(coords).tz_convert('US/Alaska')
    falldate = coords[::2]
    springdate = coords[1::2]
    fall.append(falldate)
    spring.append(springdate)
    del coords
    n += 1
    
# examine range of times
print(spring) # # average of around april 1
print(fall) # average of around mid-october
# lets go from April 1 through November 1   
    

#%%

# regression function
def regress(row,y):
    """ regress per row of dataframe, pass elevations as ys. Returns slope
    and r squared value"""
    a = stats.linregress(y,row)
    return pd.Series(a._asdict())

def lapse_2019(freq,nineteen,meta):
    """ shortcut to producing different lapse rate regressions for summer 2019
    for data with and without gates with specified resample frequency as 'freq'"""
    # format for calculations
    nnn = nineteen.resample(freq).mean()
    nnn = nnn.dropna(axis=0,how='any')# drop rows with any nans in them
    els = np.array((meta.el.gates[0],meta.el.buri[0],meta.el.usgs[0],cawsu_el)) # in m
    y = els / 1000 # change m to km for proper lapse rate units
    # apply function
    rnn = nnn.join(nnn.apply(lambda row: regress(row,y),axis=1))
    rnn['r2'] = rnn['rvalue']**2 # calculate r squared
    
    # try without Gates
    nnn = nineteen.resample(freq).mean()
    nnn = nnn.dropna(axis=0,how='any')# drop rows with any nans in them
    els = np.array((meta.el.buri[0],meta.el.usgs[0],cawsu_el)) # in m
    y = els / 1000 # change m to km for proper lapse rate units
    nnn = nnn.drop(columns=['gates'])
    # apply function
    nog = nnn.join(nnn.apply(lambda row: regress(row,y),axis=1))
    nog['r2'] = nog['rvalue']**2 # calculate r squared
    
    return rnn, nog
#%%
# --- perform high resolution lapse rate viz for summer 2019

# grab caws
caws = pd.read_pickle(os.path.join(format_data,'caws.pickle'))
cawsl_el = 675 # m elevation of root AWS
cawsu_el = 2185 # m elevation of LaChapelle AWS
# concatenate CAWS
idx=pd.IndexSlice
nineteen = pd.concat([dtvg,caws.loc[:,idx['upper','TAVG1']]],axis=1)
nineteen.columns = ['gates','buri','usgs','caws']
# 
# subset out summer 2019
start = pd.Timestamp('2019-04-01 00:00:00-0800',tz='US/Alaska')
end = pd.Timestamp('2019-10-15 00:00:00-0800',tz='US/Alaska')
s = slice(start,end) 

# --- plot all summer 2019 temp records
nnn = nineteen.resample('5D').mean()
fig,ax = plt.subplots(figsize=(10,8))
nnn.loc[s,:].plot(ax=ax,title='Summer 2019 temperatures- 5 Day averages',linewidth=4)
ax.legend()
plt.show()
    


# --- LR time series
# -------------------------------
# format 2019 data with regression, use this code block to prepare data
nga,nog = lapse_2019('W',nineteen,meta)    
# set up rest of time series data
pd.plotting.register_matplotlib_converters() # run after panda plotting
lrc = nineteen.resample('W').mean().copy()
lrc['lapse'] = 1000 * (lrc['gates'] - lrc['usgs']) / (meta.el['gates'][0] - meta.el['usgs'][0])
# ---------------------------------

# 1. plot lapse rate records on same time series
fig,ax = plt.subplots(figsize=(18,10))
ax.plot(lrc.index,lrc.lapse,color='r',linewidth=3,label='gates/usgs lapse')
ax.plot(nga.index,nga.slope,linewidth=3,color='purple',label='all 2019')
ax.plot(nog.index,nog.slope,linewidth=3,color='blue',label='w/out gates')
ax.legend()
plt.show()

# 2. plot just 2019 lapse rates
fig,ax = plt.subplots(figsize=(18,10))
ax.plot(nga.index,nga.slope,linewidth=3,color='purple',label='all 2019')
ax.plot(nog.index,nog.slope,linewidth=3,color='blue',label='w/out gates')
# just plot gates/usgs for summer 2019
ax.plot(lrx.index[s],lrc.)
ax.legend()
plt.show()  

#%%

# .....extra code........

# format for calculations
nnn = nineteen.resample('2D').mean()
nnn = nnn.dropna(axis=0,how='any')# drop rows with any nans in them
els = np.array((meta.el.gates[0],meta.el.buri[0],meta.el.usgs[0],cawsu_el)) # in m
y = els / 1000 # change m to km for proper lapse rate units
# apply function
rnn = nnn.join(nnn.apply(lambda row: regress(row,y),axis=1))
rnn['r2'] = rnn['rvalue']**2 # calculate r squared

# visualize lapse rate time series
#rnn.slope.plot(label='with gates')

# try without Gates
nnn = nineteen.resample('2D').mean()
nnn = nnn.dropna(axis=0,how='any')# drop rows with any nans in them
els = np.array((meta.el.buri[0],meta.el.usgs[0],cawsu_el)) # in m
y = els / 1000 # change m to km for proper lapse rate units
nnn = nnn.drop(columns=['gates'])
# apply function
nog = nnn.join(nnn.apply(lambda row: regress(row,y),axis=1))
nog['r2'] = nog['rvalue']**2 # calculate r squared

#nog.slope.plot(label='without gates') 
    
    
    
    
    
