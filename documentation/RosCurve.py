import pandas as pd
import math


ros = pd.read_csv('C:/FireGUARD/documentation/ros.csv')[['FFMC', 'ROS']]
ffmc = pd.read_csv('C:/Users/evensjo/OneDrive - Government of Ontario/work/fban/testFARduration/ffmc_pm.csv').set_index(['LST']).transpose()[[1500, 1700]]


r = pd.merge(ffmc, ros, left_on=1700, right_on='FFMC', how='left')[[1500, 1700, 'ROS']]
r.columns = [1500, 1700, 'ROS_1700']

s = pd.merge(r, ros, left_on=1500, right_on='FFMC', how='left')[[1500, 1700, 'ROS_1700', 'ROS']]

s.columns = [1500, 1700, 'ROS_1700', 'ROS_1500']

def find_p(x):
    return 1 / (1 + math.exp(1.64 - 0.16 * x))

s['P_1700'] = s.apply(lambda x: find_p(x['ROS_1700']), axis=1)
s['P_1500'] = s.apply(lambda x: find_p(x['ROS_1500']), axis=1)
s['pct'] = s.apply(lambda x: x['P_1500'] / x['P_1700'], axis=1)

