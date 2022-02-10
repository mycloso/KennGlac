#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 17:28:20 2021

@author: cmarkovsky
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit
from stake_class import Stake
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

directory='/Users/cmarkovsky/Desktop/AK_REU/Python/Data/'

#%% Model Class

class Model:
    
    def __init__(self, stake_folder='csv', AWS_file='ETI_Record/AWS_debris_2020_infilled_SW_Temp.csv'):
        """ Initialize a model class"""
        
        stake_files=os.listdir(directory+stake_folder)
        stake_list=[]
        stake_names=[]
        for file in stake_files:
            if not file.startswith('.'):
                stake=Stake(stake_folder+'/'+file)
                
                if not len(stake.stake_dict['Dates']) < 2:
                    stake_list.append(stake)
                    stake_names.append(stake.getname())
                    

        self.stake_list=stake_list
        self.stake_names=stake_names
        try:  
            file=pd.read_csv(directory+AWS_file)
            self.file=file
        except IOError:
            print('Could not find ', AWS_file)
        self.colors = self.construct_color_dict()
        self.get_AWS_info()
        
#%% AWS Methods
    
    def daysinbetween(self, date1, date2):
        """Calculate the number of days in between two dates"""
        
        delta=abs(date2-date1)
        return(delta.days)
        
    def changedates(self):
        """Convert dates to readible format"""
        
        self.AWS_dates=[]
        for dat in self.file['Date']:
            dt = datetime.strptime(dat, '%m/%d/%y %H:%M')
            self.AWS_dates.append(dt)
        
    def get_AWS_info(self):
        """Get data from the AWS file"""
        
        self.changedates()
        self.T=self.file['T_RTD']
        self.SW=self.file['SWin']
        self.a=.1
        self.T_t=0
        
    def determine_ele_adj(self, stake):
        """Determine the lapse rate based on elevation
           Defaults 2021 AWS, (2020) for 2020 AWS"""
        
        ele_adj=stake.temp_adj(2020)
        
        return ele_adj
    
    def get_dates(self, stake):
        """Determine the common date range for the AWS and the stake"""
        
        
        AWS_dates=self.AWS_dates
        AWS_start_date=self.AWS_dates[0]
        AWS_end_date=self.AWS_dates[-1]
        org_stake_dates=stake.dates
        
        if len(org_stake_dates) < 2:
            print('Insufficient Data')
            
        
        common_stake_dates=[date for date in org_stake_dates if date.year == AWS_start_date.year]
        common_stake_dates.sort()
        stake_start_date=common_stake_dates[0]
        stake_end_date=common_stake_dates[-1]

        if stake_start_date < AWS_start_date:
            model_start_date = AWS_start_date
        else:
            model_start_date = stake_start_date
            # print('START DATE OUT')
        
        if stake_end_date > AWS_end_date:
            model_end_date = AWS_end_date
        else:
            # print('END DATE OUT')
            model_end_date = stake_end_date
        
                
        
        model_dates=[model_start_date]

        
        if len(common_stake_dates) > 2:
            model_dates += common_stake_dates[1:-1]
        elif len(common_stake_dates) == 1:
            common_stake_dates += common_stake_dates
        model_dates.append(model_end_date)
        indicies =[AWS_dates.index(date) for date in model_dates]
        return (indicies, common_stake_dates, model_dates)

#%% Old code
        
    """Old code for iteratively determining TF and SRF"""
    # def det_act_stake_melt(self, stake):
    #     """Determine the total observed amount of melt at a stake for the date range"""
        
    #     date_info=self.get_dates(stake)
    #     indicies=date_info[0]
    #     common_stake_dates=date_info[1]
    #     model_dates=date_info[2]
    #     act_melt_total=0
    #     total_melts = []
    #     print(stake.getname())
    #     print(common_stake_dates)
    #     for i in range(len(model_dates)-1):
            
    #         index=stake.dates.index(common_stake_dates[i+1])
    #         stake_melt=stake.stake_dict['Melt'][index]
    #         total_num_days=self.daysinbetween(common_stake_dates[i], common_stake_dates[i+1])
    #         if not total_num_days == 0:
    #             melt_per_day=stake_melt/total_num_days
    #         else:
    #             melt_per_day=0
            
    #         num_model_days=self.daysinbetween(model_dates[i], model_dates[i+1])
    #         total_melt = melt_per_day * num_model_days
    #         total_melts.append(total_melt)
    #         act_melt_total += total_melt
        
    #     return (act_melt_total / 2.4, total_melts)
    
    # def get_AWS_sums(self, stake):
    #     """Determine total T and SW for the common date range"""
        
    #     inds=self.get_dates(stake)[0]
    #     new_temps=self.T[inds[0]:inds[1]]
    #     new_SW=self.SW[inds[0]:inds[1]]
    #     ele_adj=self.determine_ele_adj(stake)
    #     n=len(new_temps)
    #     act_stake_melt=self.det_act_stake_melt(stake)[0]
    #     T_sum=sum(new_temps)
    #     SW_sum=sum(new_SW)+ele_adj*n
    #     return (T_sum, SW_sum, act_stake_melt)
    

        
    # def get_step_size(self, values, itr):
    #     """Determine the step size for iterating through TF and SRF values"""

    #     min_val=values[0]
    #     max_val=values[1]
    #     diff=max_val-min_val
    #     step=diff/itr
    #     return step
    
    # def calc_melt(self, T, TF, I, SRF, a=.1, T_t=0):
    #     """Calculate melt for given conditions using M=TF*T+SRF*(1-a)*I"""
        
    #     if T > T_t:
    #         M = (float(TF)*float(T)+float(SRF)*(1-float(a))*float(I))
            
    #     else:
    #         M=0
        
    #     return M
    
    # def determine_TF_SRF(self, stake, TF_range=[0,.02], SRF_range=[0,0.001], itr=100):
    #     ## Initializing Variables
        
    #     sums=self.get_AWS_sums(stake)
    #     T_sum=sums[0]
    #     SW_sum=sums[1]
    #     act_stake_melt=sums[2]
        
    #     TF_step=self.get_step_size(TF_range, itr)
    #     SRF_step=self.get_step_size(SRF_range, itr)
        
    #     TF_array = np.empty(itr ** 2)
    #     SRF_array = np.empty(itr ** 2)
    #     melt_array = np.empty(itr ** 2)
    #     diff_array = np.empty(itr ** 2)
        
    #     best_TF = -1
    #     best_SRF = -1
    #     best_melt = -1
    #     min_diff = 10000000
        
    #     ## Iterating
        
    #     cur_TF=TF_range[0]
    #     n=0
        
    #     for i in range(itr):
            
    #         cur_SRF = SRF_range[0]
    #         for j in range(itr):
                
    #             cur_melt = self.calc_melt(T_sum, cur_TF, SW_sum, cur_SRF)
    #             diff = cur_melt-act_stake_melt
    #             if abs(diff) < min_diff:
    #                 min_diff = abs(diff)
    #                 act_diff = diff
    #                 best_TF = cur_TF
    #                 best_SRF = cur_SRF
    #                 best_melt = cur_melt
                
                
    #             TF_array[n]=cur_TF
    #             SRF_array[n]=cur_SRF
    #             melt_array[n]=cur_melt
    #             diff_array[n]=diff
                
    #             cur_SRF += SRF_step
    #             n += 1
            
    #         cur_TF += TF_step
        
    #     if T_sum == 0:
    #         DDF = 0
    #     else:
    #         DDF = act_stake_melt/T_sum
        
    #     if SW_sum == 0:
    #         SWDF = 0
    #     else:
    #         SWDF = best_melt/SW_sum
        
    #     # print('ACT', act_stake_melt)
    #     # print('DDF', DDF)
    #     # print('DDF*T_SUM', DDF*T_sum)
        
    #     arrays = [TF_array, SRF_array, melt_array, diff_array, T_sum, SW_sum]
    #     best_array = [best_TF, best_SRF, best_melt, act_stake_melt, act_diff, DDF, SWDF]
    #     if stake.if_ice():
    #         print(stake.getname(), best_array)
        
    #     return (arrays, best_array)
    
    # def construct_stake_dict(self):
    #     stake_list = self.stake_list
    #     stake_names = self.stake_names
    #     stake_dict = {}
    #     for stake in stake_list:
            
    #         model_results = self.determine_TF_SRF(stake)
    #         avg_debris_thickness = np.mean(stake_list[stake_list.index(stake)].stake_dict['Debris'])
    #         stake_dict[stake_names[stake_list.index(stake)]] = (model_results, avg_debris_thickness)
        
    #     return stake_dict
    
    

    
#%% Plotting and Graphs
    def exp(self, x, a, b):
        """Defines an exponential function: a*e^(x*b) """
        return a*np.exp(b*x)
    
    def construct_color_dict(self, random=True):
        """ Constructs a random color scheme for each stake
            NOT IN USE """
            
        color_dict = {}
        for stake in self.stake_list:
            rbg = np.random.rand(3,)
            color_dict[stake.getname()] = rbg
        
        return color_dict
        
    def temp_melt_rate_plot(self):
        """ Constructs the temperature plot and melt rate / stake"""
        
        dates = self.AWS_dates
        T = self.T
        
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        
        
        for stake in self.stake_list:
            new_stake_dates = []
            new_stake_melts = []
            for i in range(len(stake.dates)):
                if stake.dates[i].year == 2020:
                    new_stake_dates.append(stake.dates[i])
                    try:
                        new_stake_melts.append(stake.meltperday[i])
                    except:
                        pass
            for i in range(len(new_stake_dates)-1):
                
                try:
                    start_date = dates[dates.index(new_stake_dates[i])]
                except:
                    start_date = dates[0]
                try:
                    end_date = dates[dates.index(new_stake_dates[i+1])]
                except:
                    end_date = dates[-1]
                if self.daysinbetween(start_date, end_date) > 10:

                    date_list = dates[dates.index(start_date):dates.index(end_date)]
                    melt_list = new_stake_melts[i] * np.ones(len(date_list))
                    ax2.plot(date_list, melt_list, linewidth=2.0, label = stake.getname() + ' [' + '%.0f' % stake.stake_dict['Debris'][i] + ' cm]', c = self.colors[stake.getname()])
            
        
        ax1.plot(dates, T, color = 'orange')
        ax1.set_ylabel('Air Temp. (°C)')
        
        f.subplots_adjust(hspace=0)
        # ax1.plot(dates, np.average(T)*np.ones(len(T)), linestyle='--', color='k')
        
        
        # ax2.plot(dates, T)
        min_date = datetime(2020, 6, 13)
        max_date = datetime(2020, 9, 3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
        ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax2.set_ylabel('Melt Rate (cm/d)')
        ax2.set_xlim([min_date, max_date])
        ax2.set_ylim([0, 4])
        
        handles, labels = plt.gca().get_legend_handles_labels()
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        by_label = dict(zip(labels, handles))
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.7, box.height])
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0, box.width * 0.7, box.height])
        ax2.legend(by_label.values(), by_label.keys(), ncol=1, loc='upper left', bbox_to_anchor=(1, 2))
        
        # plt.savefig('exports/temp_melt_rate_plot', dpi = 300)
    
        
    def det_melt_DDFs(self):
        
        """Constructs a plot of melt rate vs. debris
            Calculates DDF for each stake
            Constructs a DDF vs. debris plot"""
            
        T = self.T
        DDF_dict ={}
        fig1 = plt.figure()
        ax1 = fig1.gca()
        
        fig2 = plt.figure()
        ax2 = fig2.gca()
        melts_per_day =[]
        
        debris_thickness_list = []
        DDFs = []
        x2 = []
        y12 = []
        y22 = []
        
        #Stake name: [Debris Thickness (cm)], [DDF (mm/dC)], [Melt rate (cm/d)] 
        stake_dict2021 = {'KAS-01': ([6], [9.153852129070337], [8.666666666666666]), 'KAS-16': ([20], [2.2854143005244354], [2.0789473684210527]), 'KAS-04': ([4.0], [7.304448185817189], [6.7105263157894735]), 'KAS-06A': ([7], [3.3443540156411773], [3.0789473684210527]), 'KAS-06B': ([10], [3.394807104089588], [3.1315789473684212]), 'P01_HOBO': ([], [], []), 'P_AWS2021_3': ([18], [2.195256066258073], [2.2439024390243905]), 'P_AWS2021_2': ([13], [2.3103321843288076], [2.3658536585365852]), 'P_AWS2021_1': ([7], [3.1336654346950823], [3.1951219512195124]), 'P_AWS_3': ([18], [0.5099601376423369], [0.5128205128205128]), 'KAS-21': ([11.5], [1.7887486253888323], [1.9305555555555556]), 'P05': ([13], [2.3187282588307077], [2.341463414634146]), 'P_AWS_2': ([6], [1.4508885608347417], [1.4615384615384615]), 'P07': ([9], [2.522804230461929], [2.5609756097560976]), 'P06': ([19], [1.7896036543524132], [1.868421052631579]), 'P_AWS_1': ([21], [1.4267419276685094], [1.435897435897436]), 'P02': ([10], [2.136112904321389], [2.3333333333333335]), 'P01': ([23], [2.309444141975733], [2.5833333333333335])}        
        
        for stake in self.stake_list: 
            date_info=self.get_dates(stake)
            indicies=date_info[0]
            common_stake_dates=date_info[1]
            model_dates=date_info[2]
            T_sums = []
            total_melts = []
            ele = self.determine_ele_adj(stake)
                    
            for i in range(len(common_stake_dates)-1):
                index=stake.dates.index(common_stake_dates[i+1])
                stake_melt=stake.stake_dict['Melt'][index]
                total_num_days=self.daysinbetween(common_stake_dates[i], common_stake_dates[i+1])
                
                if not total_num_days == 0:
                    melt_per_day=stake_melt/total_num_days
                else:
                    melt_per_day=0

                num_model_days=self.daysinbetween(model_dates[i], model_dates[i+1])
                
                # Calculates total melt (converts cm to mm)
                total_melt = melt_per_day * num_model_days * 10
                total_melts.append(total_melt)
                
                PDD = (sum(T[indicies[i]:indicies[i+1]]) + len(T[indicies[i]:indicies[i+1]])*ele) / 24
                
                T_sums.append(PDD)
                if not PDD == 0:
                    DDF_d = total_melt / PDD
                    
                else:
                    DDF_d = 0
                    
                if not DDF_d == 0:
                    melts_per_day.append(melt_per_day * 10)
                    DDFs.append(DDF_d)
                    debris_thickness_list.append(stake.stake_dict['Debris'][i])

                    if model_dates[i].month == 6 and model_dates[i+1].month == 7:
                            
                            sym = '^'
                            facecolor = 'none'
                            color = 'b'
                    elif model_dates[i].month == 7 and model_dates[i+1].month == 9:
                            
                            sym = 's'
                            facecolor = 'b'
                            color = 'b'
                            
                    if melt_per_day > 0 and total_num_days > 10:
                        
                        ax1.scatter(stake.stake_dict['Debris'][i], melt_per_day * 10, edgecolors = color, facecolors = facecolor, label = stake.getname())
                        # ax2.scatter(stake.stake_dict['Debris'][i], DDF_d, edgecolors = color, facecolors = facecolor, label = stake.getname())
                        if stake.getname() in stake_dict2021.keys():
                            for i in range(len(stake_dict2021[stake.getname()][0])):
                                ax1.scatter(stake_dict2021[stake.getname()][0][i], stake_dict2021[stake.getname()][2][i] * 10, edgecolors = 'r', facecolors = 'none')
                                x2.append(stake_dict2021[stake.getname()][0][i])
                                y12.append(stake_dict2021[stake.getname()][2][i] * 10)
                                ax2.scatter(stake_dict2021[stake.getname()][0][i], stake_dict2021[stake.getname()][1][i], edgecolors = 'r', facecolors = 'none')
                                y22.append(stake_dict2021[stake.getname()][1][i])
        
        ax1.set_xlabel('Debris Depth (cm)')
        ax1.set_ylabel('Measured Melt Rate (mm d$^{-1}$)')

        ax2.set_xlabel('Debris Depth (cm)')
        ax2.set_ylabel('Degree-Day Factor (mm d$^{-1}$ °C$^{-1}$)')
        
        # Parameters for 2020 plots (pars1: melt rate v. debris 2020), (pars12: DDF v. debris 2020)
        
        pars1, cov1 = curve_fit(f=self.exp, xdata=debris_thickness_list, ydata=melts_per_day, p0=[2.4, -.02], bounds=(-np.inf, np.inf))
        pars12, cov12 = curve_fit(f=self.exp, xdata=x2, ydata=y12, p0=[2.4, -.02], bounds=(-np.inf, np.inf))
        
        # Parameters for 2021 plots (pars2: melt rate v. debris 2021), (pars22: DDF v. debris 2021)

        pars2, cov2 = curve_fit(f=self.exp, xdata=debris_thickness_list, ydata=DDFs, p0=[2.4, -.02], bounds=(-np.inf, np.inf))
        pars22, cov22 = curve_fit(f=self.exp, xdata=x2, ydata=y22, p0=[2.4, -.02], bounds=(-np.inf, np.inf))
        
        # Parameters for 2020/2021 plots (pars13: melt rate v. debris 20/21), (pars23: DDF v. debris 20/21)

        pars13, cov13 = curve_fit(f=self.exp, xdata=debris_thickness_list + x2, ydata=melts_per_day + y12, p0=[.5, -.07], bounds=(-np.inf, np.inf))
        pars23, cov23 = curve_fit(f=self.exp, xdata=debris_thickness_list + x2, ydata=DDFs + y22, p0=[.5, -.07], bounds=(-np.inf, np.inf))
        
        # Plotting 2020 fit lines
        
        x = np.asarray(debris_thickness_list)
        x.sort()
        y1 = self.exp(x, *pars1)
        y2 = self.exp(x, *pars2)
        ax1.plot(x, y1, linestyle='--', linewidth=1, color='b', label='2020', zorder = -1)
        ax2.plot(x, y2, linestyle='--', linewidth=1, color='b', label='2020', zorder = -1)
        ax1.set_ylim([8, 92])
        ax2.set_ylim([1, 9.5])
        ax1.set_xlim([0, 24])
        ax2.set_xlim([0, 24])
        
        # Plotting 2021 fit lines
        
        x = np.linspace(4, 23)
        x.sort()
        y1 = self.exp(x, *pars12)
        y2 = self.exp(x, *pars22)
        ax1.plot(x, y1, linestyle='--', linewidth=1, color='r', label='2021', zorder=-1)
        # ax2.plot(x, y2, linestyle='--', linewidth=1, color='r', label='2021', zorder=-1)
        
        # Plotting 2020/2021 fit lines
        
        # x = np.asarray(debris_thickness_list + x2)
        # x.sort()
        # y1 = self.exp(x, *pars13)
        # y2 = self.exp(x, *pars23)
        # ax1.plot(x, y1, linestyle='--', linewidth=1, color='g', label='2020 and 2021', zorder=-1)
        # ax2.plot(x, y2, linestyle='--', linewidth=1, color='g', label='2020 and 2021', zorder=-1)
        

        # Constructs a custom list of lines for the legend
        
        custom_lines = [
                        Line2D([0], [0], linestyle='--', linewidth=1, color='b'),
                        
                        
                        
                        
                       
                        Line2D([0], [0], marker='o', color='w', markeredgecolor = 'r')
                        
                        
                        
                        ]       
        ax1.legend(custom_lines, ['2020 Season', '2021 Season', 'Jun. – Jul.', 'Jul. – Sep.'], fontsize = 8)
        
        ax2.legend(custom_lines, ['2020 Season', 'Jun. – Jul. 2021' ], fontsize = 8)


        # fig1.savefig('exports/melt_rate_final_20_21', dpi = 300)
        fig2.savefig('exports/DDF_debris_final_early_21', dpi = 300)
        
        return DDF_dict
        
        
        
        
            
    
            
        
        
        
#%% Main Function
        
def main():
    model = Model('csv_debris')
    model.temp_melt_rate_plot()
    model.det_melt_DDFs()
    
    
#%% Main

main()