#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:54:34 2019

@author: raghav, lau

#Largely based on Augmento's code at https://github.com/augmento-ai/quant-reseach
#Purpose is to reproduc Augmento's "Positive/Bearish" sentiment indicator that claims to give a very decent profit in BTC from 2017 - 2019
"""

#import sys
import requests
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from pandas.io.json import json_normalize
import pandas as pd

import analysis_helper as ah

# define the urls of the endpoints for topics
topics_endpoint_url = "http://api-dev.augmento.ai/v0.1/topics"  

# save a list of the augmento topics
r_topic = requests.request("GET", topics_endpoint_url, timeout=10)

temp_topic_data= r_topic.json()

data_topic = json_normalize(temp_topic_data).T
data_topic.columns = ['Labels']

bearish_index= data_topic.index[data_topic['Labels'] == 'Bearish'].values
positive_index= data_topic.index[data_topic['Labels'] == 'Positive'].values

# define the url of the endpoint to get event data
endpoint_url = "http://api-dev.augmento.ai/v0.1/events/aggregated"

# define the start and end times
datetime_start = datetime.datetime(2017, 1, 1)
datetime_end = datetime.datetime.now()
        
# initialise a store for the data we're downloading
sentiment_data = pd.DataFrame()

# define a start pointer to track multiple requests
start_ptr = 0
count_ptr = 1000

# get the data
while start_ptr >= 0:
    headers = {"api-key" : "LWn2e7VeXDtoANEvSgYZ"}
	# define the parameters of the request
    params = {
        "source" : "twitter",
		"coin" : "cardano",
		"bin_size" : "1H",
		"count_ptr" : count_ptr,
		"start_ptr" : start_ptr,
		"start_datetime" : datetime_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
		"end_datetime" : datetime_end.strftime("%Y-%m-%dT%H:%M:%SZ")
	}
	
	# make the request
    r = requests.request("GET", endpoint_url, params=params, headers=headers, timeout=10)
	
	# if the request was ok, add the data and increment the start_ptr
	# else return an error
    if r.status_code == 200:
       temp_data = r.json()
       if len(temp_data) == 0:
           start_ptr = -1
       else:
           data = json_normalize(temp_data)
           #data['datetime'] = str(data['datetime'])
           labels = data['counts'].apply(pd.Series)
           # rename each variable is tags
           data_topic.index[data_topic['Labels'] == 'Bearish'].values
           labels = labels.rename(columns = lambda x :temp_topic_data[str(x)])
           data = pd.concat([data[:], labels[:]], axis=1)
           tmp = data.drop('counts',axis=1)
           #final_data = data[['Label_'+''.join(bearish_index),'Label_'+''.join(positive_index),'datetime','t_epoch']]
           #sentiment_data=sentiment_data.append(tmp)
           sentiment_data=sentiment_data.append(tmp)
           start_ptr += count_ptr
    else:
       raise Exception("api call failed with status_code {:d}".format(r.status_code))
    
    # if we didn't get any data, assume we've got all the data
    if len(temp_data) == 0:
       start_ptr = -1
    
    # sleep
    time.sleep(2.0)
    
    sentiment_data.to_csv('ADArd_2017_to_now.csv')

aaa = sentiment_data[['Label_'+''.join(positive_index)]].values.tolist()
aug_signal_a = np.array([float(i) for sublist in aaa for i in sublist])
bbb = sentiment_data[['Label_'+''.join(bearish_index)]].values.tolist()
aug_signal_b = np.array([float(i) for sublist in bbb for i in sublist])
ttt = sentiment_data[['t_epoch']].values.tolist()
t_aug_data = [int(i) for sublist in ttt for i in sublist]

window_size_A = 28
window_size_B = 14

# generate the sentiment score
sent_score = ah.nb_calc_sentiment_score_a(aug_signal_a, aug_signal_b, window_size_A, window_size_B)
#sent_score = ah.nb_calc_sentiment_score_c(aug_signal_a, aug_signal_b, window_size, window_size)

#notification signals based on sent_score

notification = 'neutral'

if sent_score[-1] > 0.0:
    notification = 'long'
elif sent_score[-1] <= 0.0:
	notification = 'short'
elif sent_score[-1] == 0.0:
	notification = 'neutral'
    
print(notification)

# set up the figure
fig, ax = plt.subplots(3, 1, sharex=True, sharey=False)

# initialise some labels for the plot
datenum_aug_data = [md.date2num(datetime.datetime.fromtimestamp(el)) for el in t_aug_data]
#datenum_price_data = [md.date2num(datetime.datetime.fromtimestamp(el)) for el in t_price_data]

# plot stuff
#ax[0].grid(linewidth=0.4)
#ax[1].grid(linewidth=0.4)
#ax[2].grid(linewidth=0.4)
#ax[0].plot(datenum_price_data, price_data, linewidth=0.5)
#ax[1].plot(datenum_aug_data, sent_score, linewidth=0.5)
#ax[2].plot(datenum_price_data, pnl, linewidth=0.5)

# label axes
#ax[0].set_ylabel("Price")
#ax[1].set_ylabel("Seniment score")
#ax[2].set_ylabel("PnL")
#ax[1].set_ylim([-5.5, 5.5])

#ax[0].set_title("4_basic_strategy_example.py")

# generate the time axes
#plt.subplots_adjust(bottom=0.2)
#plt.xticks( rotation=25 )
#ax[0]=plt.gca()
#xfmt = md.DateFormatter('%Y-%m-%d')
#ax[0].xaxis.set_major_formatter(xfmt)

# show the plot
#plt.show()
