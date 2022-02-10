#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 14:49:02 2021

@author: cmarkovsky
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math


#%% Stake Class

class Stake:

    
    def __init__(self, filename):
        self.filename=filename
        directory='/Users/cmarkovsky/Desktop/AK_REU/Python/Data/'
        file=pd.read_csv(directory+self.filename)
        self.file=file
        self.getstakeinfo()
        self.meltperday()

        
    
    def getstakeinfo(self):
        stake=self.file
        stake_dict={}
        stake_dict['Dates']=stake['Date']
        stake_dict['Melt']=stake['Melt']
        stake_dict['Debris']=stake['Debris Depth (cm)']
        stake_dict['Ele']=stake['Elevation(m)']
        stake_dict['Surface']=stake['Surface Type'][0]
        self.stake_dict=stake_dict
        dates=self.stake_dict['Dates']
        new_dates=[]
        for m in range(len(dates)):
            new_dates.append(self.datechange(dates[m]))
        self.dates=new_dates    
        return stake_dict

    def datechange(self, str1):
    # str1=str(str1)

        dt = datetime.strptime(str1, '%m/%d/%y')
       
        return(dt)

    def daysinbetween(self, date1, date2):
        delta=abs(date2-date1)
        return(delta.days)

    def meltperday(self):
        totalmelt=[]
        melt=self.stake_dict['Melt']
        daymelt_list=[] #(#Days, Melt)
        for m in range(len(self.dates)-1):
            day1=self.dates[m]
            day2=self.dates[m+1]
            num_days=self.daysinbetween(day1, day2)
            daymelt_list.append(float(melt[m+1])/num_days)
            totalmelt.append(melt[m+1])
        self.meltperday=daymelt_list
        self.totalmelt=totalmelt
        return daymelt_list

    def elevation(self):
        ele_list=self.stake_dict['Ele']
        ele=0
        # print(ele_list)
        for item in ele_list:
            if item > 0:
                ele=item
                return(ele)
            else:
                ele=-1
        self.ele=ele 
        
        return(ele)

    def temp_adj(self, AWS):
        ele=self.elevation()
        
        if AWS == 2021:
            standard = 541
        else:
            standard = 585.8

        fact=-6.5*(ele-standard)/1000
        return fact
    
    def dates(self):
        info=self.csv()
        return info['Date']

    def plotmvd(self, dates, melts):
        fig=plt.figure()
        ax=fig.gca()
        ax.grid()
        plt.plot(dates, melts)
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylabel('Melt Rate (cm/day)')
        
    def melt_sum(self):
        total_melt=sum(self.totalmelt)
        return total_melt
    
    def getname(self):
        filename=self.filename
        name=filename[filename.index("/")+1:filename.index(".")]
        self.name=name
        return name
    
    def if_ice(self):
        if self.stake_dict['Surface'] == 'Ice':
            return True
        else:
            return False
        
    
    
        
    
