# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 16:47:34 2020

@author: tamaral
"""
# =========================
# MANAGE STAKE DATA
# EXTRAPOLATE TEMPS
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

#%%


