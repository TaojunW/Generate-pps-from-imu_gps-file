# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:07:56 2020

@author: wang3241
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from decimal import *
import scipy.interpolate

# Global variables
next_msg      = 'Start'
section_start = datetime.now()
x = section_start

def trace(txt):
    '''Log timing, progress, and info to stdout'''

    global section_start, next_msg, wng

    section_end   = datetime.now()
    print('%5s %s' % (str(section_end - section_start)[2:7],next_msg))
    section_start = section_end
    next_msg      = txt
    
def time_delay_fun(pps, imu_gps):
    Time_gpsimu = [datetime.strptime(i, '%Y/%m/%d %H:%M:%S.%f').time() for i in imu_gps['Gps_UTC_DateTime'][1:]]
    Time_gpsimu_SEC = np.array([i.hour*3600.0+i.minute*60.0+i.second+10e-7*i.microsecond for i in Time_gpsimu])
    time_delay_m = np.zeros((len(pps)-1, 4))
    time0 = np.ceil(Time_gpsimu_SEC[0]);
    dpps = pps[1:] - pps[:-1]
    #dpps_med = np.median(dpps)
    dpps_med = np.mean(dpps)
    time_delay_m[0,3] = pps[0]
    for i in range(len(pps)-1):
        index0 = np.where(Time_gpsimu_SEC == time0+i)[0]
        index1 = np.where(Time_gpsimu_SEC == time0+i+1)[0]
        timetag0 = imu_gps['Timestamp'][index0+1];
        if len(timetag0)==0:
            p_closest_ts = np.argmin(np.abs(Time_gpsimu_SEC-(time0+i)))
            v_closest_ts = Time_gpsimu_SEC[p_closest_ts]
            if v_closest_ts > time0+i:
                index1_1 = p_closest_ts-1;
                index1_2 = p_closest_ts;
            else:
                index1_1 = p_closest_ts;
                index1_2 = p_closest_ts+1;
            ratio_ts = ( (time0+i) - Time_gpsimu_SEC[index1_1] ) / ( Time_gpsimu_SEC[index1_2] - Time_gpsimu_SEC[index1_1] );
            timetag0 = imu_gps['Timestamp'][index1_1+1] + ratio_ts * (imu_gps['Timestamp'][index1_2+1]-imu_gps['Timestamp'][index1_1+1]);
        timetag1 = imu_gps['Timestamp'][index1+1];
        if len(timetag1)==0:
            p_closest_ts = np.argmin(np.abs(Time_gpsimu_SEC-(time0+i+1)))
            v_closest_ts = Time_gpsimu_SEC[p_closest_ts]
            if v_closest_ts > time0+i+1:
                index1_1 = p_closest_ts-1;
                index1_2 = p_closest_ts;
            else:
                index1_1 = p_closest_ts;
                index1_2 = p_closest_ts+1;
            ratio_ts = ( (time0+i) - Time_gpsimu_SEC[index1_1] ) / ( Time_gpsimu_SEC[index1_2] - Time_gpsimu_SEC[index1_1] );
            timetag1 = imu_gps['Timestamp'][index1_1+1] + ratio_ts * (imu_gps['Timestamp'][index1_2+1]-imu_gps['Timestamp'][index1_1+1]);    
        time_delay_m[i,0] = time0+i;
        time_delay_m[i,1] = np.divide(timetag0-pps[i],timetag1-timetag0);
        time_delay_m[i,2] = dpps_med
        if i>0:
            time_delay_m[i,3] = time_delay_m[i-1,3]+dpps_med
        time_delay_m[:,3] = np.round(time_delay_m[:,3])
    return time_delay_m

########### read old imu gps file and pps file ###########
trace('Read imu gps data')
with open('./20180529_old_pps/imu_gps.txt','r') as fd:
    imu_gps = np.genfromtxt(fd,delimiter='\t',skip_header=1, skip_footer=1, 
        dtype = {'names'  : ('Roll' ,'Pitch','Yaw'  ,'Lat'  ,'Lon'  ,'Alt'  ,'Timestamp','Gps_UTC_DateTime')
                ,'formats': ('float','float','float','float','float','float','float'    , 'U50'             )})
print(imu_gps['Gps_UTC_DateTime'])
print(type(imu_gps['Gps_UTC_DateTime']))
trace('GPS UTC date & time: '+imu_gps['Gps_UTC_DateTime'][0])

trace('Read frame pps data')
pps = np.loadtxt('./20180529_old_pps/pps.txt', skiprows=1)

trace('Calculating time delay using pps')
time_delay_m = time_delay_fun(pps, imu_gps)
f = plt.figure(figsize = (100,20))
ax1 = f.add_subplot(1,1,1)
plt.title('Delay from PPS', fontsize=50)
plt.xlabel('time (sec)', fontsize=50)
plt.ylabel('delay (milisec)', fontsize=50)
a = ax1.plot(time_delay_m[:,0], 1000.0 * time_delay_m[:,1], linewidth=10)
plt.savefig('delay_pps', bbox_inches='tight', pad_inches=0.2)
plt.close()

################## read new imu gps file ############
print('Mean of old time delay: %f'%np.mean(time_delay_m[:,1]))
print('Std of old time delay: %f'%np.std(time_delay_m[:,1]))

trace('Read imu gps data')
with open('./banding_test1/100136_20200512_banding_test_2020_05_12_16_24_49/imu_gps.txt','r') as fd:
    new_imu_gps = np.genfromtxt(fd,delimiter='\t',skip_header=1, skip_footer=1, 
        dtype = {'names'  : ('Roll' ,'Pitch','Yaw'  ,'Lat'  ,'Lon'  ,'Alt'  ,'Timestamp','Gps_UTC_DateTime')
                ,'formats': ('float','float','float','float','float','float','float'    , 'U50'             )})
print(new_imu_gps['Gps_UTC_DateTime'])
print(type(new_imu_gps['Gps_UTC_DateTime']))
trace('GPS UTC date & time: '+new_imu_gps['Gps_UTC_DateTime'][0])

Time_gpsimu = [datetime.strptime(i, '%Y/%m/%d %H:%M:%S.%f').time() for i in new_imu_gps['Gps_UTC_DateTime'][1:]]
Time_gpsimu_SEC = np.array([i.hour*3600.0+i.minute*60.0+i.second+10e-7*i.microsecond for i in Time_gpsimu])

find_sec = np.floor( (1 - np.mean(time_delay_m[:,1])) * 100 )/ 100
sec_x = np.array([find_sec , find_sec + 0.01])

new_pps = np.empty([1,])

for i in range(len(Time_gpsimu_SEC)-2):
    getcontext().prec = 4
    decimal_num = float(Decimal(Time_gpsimu_SEC[i]) - Decimal(np.floor(Time_gpsimu_SEC[i])))
    if decimal_num == find_sec:
        timestamp_y = np.array([new_imu_gps['Timestamp'][i+1], new_imu_gps['Timestamp'][i+2]])
        y_interp = scipy.interpolate.interp1d(sec_x, timestamp_y)
        new_pps = np.append(new_pps, int(np.around(y_interp( 1 -  np.mean(time_delay_m[:,1])))))       

new_pps = new_pps[1:]
np.savetxt('new_pps.txt', new_pps, fmt='%d', header='Timestamp')

trace('Read new pps data')
new_time_delay_m = time_delay_fun(new_pps, new_imu_gps)
f = plt.figure(figsize = (100,20))
ax1 = f.add_subplot(1,1,1)
plt.title('Delay from PPS', fontsize=50)
plt.xlabel('time (sec)', fontsize=50)
plt.ylabel('delay (milisec)', fontsize=50)
a = ax1.plot(new_time_delay_m[:,0], 1000.0 * new_time_delay_m[:,1], linewidth=10)
plt.savefig('new_delay_pps', bbox_inches='tight', pad_inches=0.2)
plt.close()
