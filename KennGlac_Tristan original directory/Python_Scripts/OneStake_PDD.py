# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 16:47:34 2020

@author: tamaral
"""
# =========================
# TAKE ONE STAKE THROUGH
# WHOLE PROCESS
# =========================


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
lr = -4.11 # c/km - derived from LR_Exploration median value
#%%
# ----------
# melt model
# ----------

# --- stake variables
kl_el = 790 # meters
kl_spring = pd.Timestamp('2019-06-07',tz='US/Alaska') # date of spring visit
kl_fall = pd.Timestamp('2019-08-22',tz='US/Alaska') # date of fall visit
kl_swe = 5.28 # m w.e. ice ablated between visits. 
usgs_el = 409 # meters,  appr. elevation of usgs gage station

# --- construct synthetic temp time series
# load usgs data
dtvg = pd.read_pickle(os.path.join(format_data,'daily_tavg.pickle')) # read in temperature data w/ filled usgs record
dtvg.columns # just tavg for usgs, buri, and gates
# grab data from extended ablation season ... these are flexible!
start = pd.Timestamp('2019-03-01',tz='US/Alaska')
end = pd.Timestamp('2019-11-01',tz='US/Alaska')
# construct dataframe with usgs, extrapolated stake temperature records
kl = pd.DataFrame(index=pd.date_range(start,end,freq='D'))
kl['usgs'] = dtvg.loc[slice(start,end),'usgs'] # grab usgs temperatures
site_diff = (kl_el - usgs_el) / 1000 # convert to km
kl['stake'] = kl.usgs + (lr * site_diff) # calculate synthetic stake temps

# plot temperature records to check
plt.figure(figsize=(10,8))
kl.usgs.plot(label='usgs')
kl.stake.plot(label='stake')
plt.legend()
plt.show()

# --- fit ice melt rate parameter (a = dd*ki)
dddf = kl.loc[slice(kl_spring,kl_fall),'stake'] # new dataframe for just days between visits (inclusive of visit days)
dd = dddf.loc[dddf > 0].sum() # sum degree days
ki = (kl_swe * 1000) / dd   # units mm / d*C


print( 'Degree day ice factor for Kenn Low stake ({0} m) for summer 2019 is {1:.2f} mm/d*C'
      .format(kl_el,ki))

# ---- Modeled ice ablation records
kl['dd'] = kl['stake'].where(kl['stake'] > 0, 0) # columns of individual degree days
kl['cumdd'] = kl['dd'].cumsum() #  cumulative DD column
kl['cumabl'] = kl['cumdd'].multiply(ki / 1000) # cumulative ablation column (meters)
kl['abl'] = kl['cumabl'].diff().multiply(1000) # daily ice ablation in mm

# ---- Modeled + empirical ice ablation (For when DDF has some error...)
pre_visit = kl.loc[(kl_spring - pd.Timedelta(1,'D')),'cumabl'] # m of modeled ice melt before spring visit, not counting visit day
post_visit = kl.loc[end,'cumabl'] - kl.loc[kl_fall,'cumabl']# m of modeled ice melt post visit, not counting visit day
full_season = pre_visit + kl_swe + post_visit # add in empirical ice melt b/w visits


# plot cumulative and daily melt 
fig,ax = plt.subplots(figsize=(8,8))
ax.set_title('Modeled Ice Ablation at Kenn Lo 2019')
kl.cumabl.plot(ax=ax,linewidth=4,color='steelblue')
ax.set_ylabel('Cumulative Ice Melt (m)')
# plot daily melt
ax2 = ax.twinx()
ax2.set_ylabel('Daily Ice Melt (mm)')
kl.abl.plot(ax=ax2,linewidth=2,color='gray')
plt.show()
