#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 10:47:01 2020

@author: admin
"""

#=====================================
# Calculate Environmental LR
# using met data dfs from 
# Met_data_import script
#=====================================

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.lines import Line2D
# set up
pd.plotting.register_matplotlib_converters()
plt.style.use('ggplot')

# data folder
data = '/Users/admin/Desktop/GIP-2020/Kennicott/DATA/'
figure_folder = '/Users/admin/Desktop/GIP-2020/Kennicott/PRODUCTS/Python_Figures'
format_data = '/Users/admin/Desktop/GIP-2020/Kennicott/PROJECT/FormattedData'

#%%
# --- Load Data
meta = pd.read_pickle(os.path.join(format_data,'temperature_meta.pickle'))
dd = pd.read_pickle(os.path.join(format_data,'daily_temperature_data.pickle'))
hr = pd.read_pickle(os.path.join(format_data,'hourly_temperature_data.pickle'))

#%%
# -------------------------
# Quick plotting Functions
# -------------------------
def timesubplots(df):
    """Takes in dataframe with varying number of keys and plots each 
    temperature variable for each station (key). Assumes indexes are dates."""
    
    # get df dimensions and key names
    sites,vals = [],[]
    for key in df.keys():
        sites.append(key[0])
        vals.append(key[1])
    sites = pd.Series(sites).unique()
    vals = pd.Series(vals)
    vals = vals[vals!='TAVG'].unique()
    names = {'gates':'Gates Glacier','may':'May Creek','buri':'Buri AWS',
            'usgs': 'USGS Gage','coop': 'NWS Coop'}
    
    # plotting parameters
    fig,axs = plt.subplots(len(sites),1,sharex=True,figsize=(11,9))
    colors = ['mediumblue','indianred']
    
    # loop plotting
    for site,ax in zip(sites,axs): # for each subplot
        ax.set_title(names[site])
        for c,t in zip(colors,vals): # for each temp parameter
            ax.plot(df[site].index,df[site][t],color=c)

    # make labels
    ax = fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax.set_xlabel('DATE', labelpad=10,size=16) # Use argument `labelpad` to move label downwards.
    ax.set_ylabel('Air Temperature (C)', labelpad=20,size=16)
    
    # legend
    lines = [Line2D([0],[0],color=colors[0],lw=3),
             Line2D([0],[0],color=colors[1],lw=3)]
    ax.legend(lines,['TMIN','TMAX'],loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.grid(True)
    plt.tight_layout(.1)
    plt.show()
    
#%%
# ========================
# Temperatures Exploration
# =========================

# dd has tmin, tavg, tmax for gates, may, buri, usgs, coop

# resample to different intervals
ww = dd.resample('W').mean()
bw = dd.resample('SM').mean() # semi-monthly
mm = dd.resample('M').mean() # monthly
# too coarse
qu = dd.resample('Q').mean() # by quarter

# 1.  Stacked monthly plot
fig, ax = plt.subplots(figsize=(15,9))
ax.set_title('Seasonal TAVG', fontsize=16)
# iterators
keys = ['gates','may','buri','usgs','coop']
colors = [cm.jet(x) for x in np.linspace(0,1,5)]

for key,c in zip(keys,colors):
    ax.plot(mm.group[key].TAVG,label=key,color=c)
    ax.plot(mm_group[key].TAVG,label=key,color=c)
ax.legend()
plt.show()
    
# --- Create nicer index labels
# 1. Conventional seasonal scale
# create dictionary of months/seasons
quarters = {
    'winter': [12, 1, 2],
    'spring': [3, 4, 5],
    'summer': [6, 7, 8],
    'fall': [9, 10, 11]}
# assign each month number to a season string
months = {month: season for season in quarters.keys()
                        for month in quarters[season]}
# append new index of strings
qu = qu.set_index(pd.Series(qu.index.month).map(months) +
                   ' ' + qu.index.year.astype(str),append=True)

# 2. Create custom alaska seasons
seasons = {'summer': [5,6,7,8,9], # May - September
           'winter': [1,2,3,4,10,11,12]}
months = {num:sea for sea in seasons.keys()
                        for num in seasons[sea]}
seaidx = pd.Index(pd.Series(mm.index.month).map(months)+
                  ' ' + mm.index.year.astype(str),name='SEASON')
mm = mm.set_index(seaidx,append=True)
# 3. Monthly index by name
# set new index
names = ['','January','February','March','April','May','June',
          'July','August','September','October','November','December']
months = {i:name for i,name in enumerate(names)}

# 3. create and name new index, then append
newidx = pd.Index(pd.Series(mm.index.month).map(months),name='MONTH')
mm = mm.set_index(newidx,append=True)
mm = mm.T

# --- Pivot and Plotting
# groupby season, then plot by season


mm.xs(key='winter 2016',level='SEASON').unstack().loc[:,'TAVG']


mm_group = mm.groupby(level='SEASON')

years = ['2016','2017','2018','2019','2020']
fig,axs = plt.subplots(2,2,figsize=(10,9))
sites = ['gates','may','buri','usgs','coop']
colors = [cm.jet(x) for x in np.linspace(0,1,5)]
# summer plot
for year,ax in zip(years,axs.flatten()): # for each subplot
    for site,c in zip(sites,colors):
        
        key = 'summer '+year
        temp = pd.DataFrame(mm.xs(key=key,level='SEASON').unstack().loc[:,'TAVG'])
        ax.set_title = key
        temp.loc[[site]]
        

plt.show()

# working with temp
# name both index cols
temp.index.set_names(['SITE','DATE'],inplace=True)
# name temperature column
temp.columns = ['TAVG']

# pivot for plotting
temp.reset_index().pivot(index='DATE',columns='SITE',values='TAVG').plot(title='TAVG',linewidth=3)

# try with all variables. this works, but does one season at a time
# isolate a summer, unstack to get sites and temps as index, 
# then unstack again to return Temps to columns
summer = pd.DataFrame(mm.xs(key='summer 2019',
                            level='SEASON').unstack().unstack(level=1))
# gives me three index, so rename and pivot
summer.index.set_names(['SITE','DATE'],inplace=True)
# pivot to get sites as columns for plotting

fig,axs = plt.subplots(1,3,sharey=True,figsize=(15,9))
vars = ['TMIN','TMAX','TAVG']
plt.xticks(rotation='horizontal')
for var,ax in zip(vars,axs.flatten()):
    summer.reset_index().pivot(index='DATE',columns='SITE',values=var).plot(
        ax=ax,title=var,linewidth=3,x_compat=True)
    #ax.xaxis.set_major_locator(mdates.MonthLocator())
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%b')) # just put month abbr
    ax.set_xlabel('')
   
# common labels
fig.add_subplot(111, frame_on=False)
plt.tick_params(labelcolor="none", bottom=False, left=False)
plt.xlabel('Summer 2019',fontsize=16)
plt.ylabel('Temperature (C)',fontsize=16)
plt.show()
#summer_pivot = summer.reset_index().pivot(index='DATE',columns='SITE')


#%%
#--- Concise seasonal plotting

# resample to different intervals
td = dd.resample('3D').mean()
ww = dd.resample('W').mean() # closed to right (end of week)
bw = dd.resample('SM').mean() # semi-monthly
mm = dd.resample('M').mean() # monthly

# construct new custom AK summer index
def AK_ix(df):
    """ constructs new index for alaska summer that goes from
    May 1 to September 30. """
    
    seasons = {'summer': [4,5,6,7,8,9], # May - September
               'winter': [1,2,3,10,11,12]}
    months = {num:sea for sea in seasons.keys()
                            for num in seasons[sea]}
    # name winter according to year which it starts
    sea = pd.Series(df.index.month).map(months)+' ' + df.index.year.astype(str)
    # move winter years back
    for date,lab,i in zip(df.index.get_level_values(0),sea,np.arange(len(sea))):
        if date.month < 4: # subtract one from year..
            new = lab.split()[0]+ ' ' + str(int(lab.split()[1])-1)
            sea.iloc[i] = new
    # put back into dataframe
    seaidx = pd.Index(sea,name='SEASON')
    df = df.set_index(seaidx,append=True)
    
    return df
#%%
# --- re-arrange dataframe and plot
td = AK_ix(td)
#ww.index # view to check
summer_plots(td)
def summer_plots(df):
    
    # slice into summers 
    years = ['2016','2017','2018','2019','2020']
    for year in years:
        key = 'summer '+ year
        
        # subset out one season of data
        summer = df.xs(key=key,level='SEASON').unstack().unstack(level=1)
        
        # reshape and rename for plotting
        summer.index.set_names(['SITE','DATE'],inplace=True)
        
        # plot all variables
        fig,axs = plt.subplots(1,3,sharey=True,figsize=(14,8))
        fig.suptitle(key,fontsize=18)
        fig.subplots_adjust(top=0.88)
        
        vars = ['TMIN','TMAX','TAVG']
        plt.xticks(rotation='horizontal')
        for var,ax in zip(vars,axs.flatten()):
            summer.reset_index().pivot(index='DATE',columns='SITE',values=var).plot(
                ax=ax,title=var,linewidth=3)
            #ax.xaxis.set_major_locator(mdates.MonthLocator())
            #ax.xaxis.set_major_formatter(mdates.DateFormatter('%b')) # just put month abbr
            ax.set_xlabel('')
            
        # common labels
        fig.add_subplot(111, frame_on=False)
        plt.tick_params(labelcolor="none", bottom=False, left=False)
        plt.ylabel('Temperature (C)',fontsize=16)
        plt.show()

#%%
#----- Average of four summers temperatures
def lapse_summers(df):
    
    # slice into summers 
    years = ['2016','2017','2018','2019','2020']
    for year in years:
        key = 'summer '+ year
        
        # subset out one season of data
        summer = df.xs(key=key,level='SEASON').unstack().unstack(level=1)
        
        # reshape and rename for plotting
        summer.index.set_names(['SITE','DATE'],inplace=True)
        
        # plot all variables
        fig,axs = plt.subplots(1,3,sharey=True,figsize=(14,8))
        fig.suptitle(key,fontsize=18)
        fig.subplots_adjust(top=0.88)
        
        # make new lapse rate variable
        
        vars = ['TMIN','TMAX','TAVG']
        plt.xticks(rotation='horizontal')
        for var,ax in zip(vars,axs.flatten()):
            summer.reset_index().pivot(index='DATE',columns='SITE',values=var).plot(
                ax=ax,title=var,linewidth=3)
            #ax.xaxis.set_major_locator(mdates.MonthLocator())
            #ax.xaxis.set_major_formatter(mdates.DateFormatter('%b')) # just put month abbr
            ax.set_xlabel('')
            
        # common labels
        fig.add_subplot(111, frame_on=False)
        plt.tick_params(labelcolor="none", bottom=False, left=False)
        plt.ylabel('Temperature (C)',fontsize=16)
        plt.show()

#%%
ww = dd.resample('W').mean()
# put in season index

ww = AK_ix(ww)

# try adding lapse rate column in for each site
# one summer at a time
        
slr = ww.xs(key='summer 2016',level='SEASON').unstack().unstack(level=1)
wwlr = ww.reset_index().pivot(index='DATE',columns='SITE',values=['TMAX'])

# how to swap index levels of columns
sites = ww.columns.get_level_values(0)
tvars = ww.columns.get_level_values(1)
ww = ww.swaplevel(axis=1) # puts tvars first, then sites

# make new lr columns
for site in sites.unique():
    ww[site,'lr'] = pd.Series(dtype='float64')
ww = ww.sort_index(axis=1) # put sites back together

# reformat metadata index, get rid of zeros
meta = meta.reset_index(level=1,drop=True)
# create function to apply to lr columns usig np.where
# can also use map, apply, or df.iterrows

# if coop: LR per km
lr1 = 1000* (ww[site].TMAX - ww.coop.TMAX) / (meta.el[site] - meta.el.coop)
lr2 = 1000* (ww[site].TMAX - ww.usgs.TMAX) / (meta.el[site] - meta.el.usgs)
# iterate through sites
for site in sites.unique():
    ww[site,'lr'] = np.where(ww.index.year in ['2016','2017'],[lr1,lr2])
    
# then do AK index
ww = AK_ix(ww)    
    

#%%
# ==============
# LR Exploration
# ==============
























 