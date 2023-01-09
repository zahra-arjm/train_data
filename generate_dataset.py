#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python code for generating train-passenger data
"""

# you can install conda environment with this terminal command
# conda env create --name dataviz --file environment.yml

#set up environment


def arrival_times_in_range(range_hours, arrival_times):
  arrival_times_in_range = arrival_times[np.where(np.logical_and(arrival_times>=range_hours[0], arrival_times<=range_hours[1]))]
  return arrival_times_in_range


def update_journey_freq_day(hist_bins, arrival_times, train_route_time_zip, journey_freq_day):
    # find train-time which fits within each bin of the histogram
  for bin_i in range(len(hist_bins)-1):
    t_time = arrival_times[np.where(np.logical_and(arrival_times>=hist_bins[bin_i], arrival_times<=hist_bins[bin_i+1]))]
    # find index of the journey in the list of tuples of journeys if t_time is not empty
    if len(t_time):
      t_idx = [idx for idx, tup in enumerate(train_route_time_zip) if tup[2] == t_time]
      # set frequency of the journey to histogram count if t_idx is not empty
      if len(t_idx): 
        journey_freq_day[t_idx[0]] += counts[bin_i]
  return journey_freq_day


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import datetime

#set seed for reproducability 
np.random.seed(202211)
random.seed(202211)

#number of passengers per weekday
passenger_n = 10000
# maximum capacity of the train
max_capacity = 500

#possible routes
routes = ['A', 'B', 'C', 'D', 'E']

# number of trains; number of routes multiplied by 2
train_n = len(routes) * 2
#generate train id
train_id = list(np.arange(train_n) + 1)
#transform integers to strings and add t0
train_id = ["t0" + str(int(x)) if x < 10 else "t" + str(int(x)) for x in train_id]
random.shuffle(train_id)

#number of journeys per day for each route (between 1 and 20)
journey_per_route_n = [np.random.randint(1,20) for x in routes]

# keep journey time in list of lists
journey_times = []
# keep all the train times
arrival_times = []
# generate uniformly distributed hours for each route throughout the day with random start and end (from 6 am to 11 pm plus minus 1 hour)
for route_i in range(len(routes)):
  route_i_times = list(np.linspace(start=6+((np.random.rand())*2 - 1), stop=(23+((np.random.rand())*2 - 1)), num=journey_per_route_n[route_i]))
  journey_times.append(route_i_times)
  arrival_times.extend(route_i_times)

arrival_times = np.array(arrival_times)
arrival_times.sort()

route_i = 0
train_route_time_zip = []
#assign each train to a route and time
for route_i_times in journey_times:
  journey_i = 0
  for time in route_i_times:
    # iterate between the two trains assigned to a route
    if journey_i % 2 == 0:
      train = train_id[(route_i-1)*2 + 1]
    else:
      train = train_id[(route_i-1)*2 + 2]
  # zip train id, route and time -> one journey
    train_route_time_zip.append((train, routes[route_i], time))
    journey_i += 1

  route_i += 1



# create 7 days before 25/11/2022
base = datetime.date(2022, 11, 25)
date_list = [base - datetime.timedelta(days=x+1) for x in range(7)]

# the plan is to build three separate uniform distributions and add them to build the dataset.
# the two rush hours on mornings and nights each one get part of the commuters; the rest will be spreaded out 
# during the whole day

# proportion of passengers in weekday compared to the day total commuters
rush_morning_per = .4
rush_night_per = .3
# proportion of passengers in weekends compared to weekdays
weekend_per = .25

# empty list of frequencies for all journeys
journey_freq = [[0] * len(train_route_time_zip) for _ in range(len(date_list))]

range_rush_morning = (7, 10)
rush_morning_arrivals = arrival_times_in_range(range_rush_morning, arrival_times)

for day in range(len(date_list)):
  #skip weekends!
  if date_list[day].weekday() >= 5:
    continue
# make each day unique by setting a different seed
  np.random.seed(2022+day)
  # number of bins, such that each bin only contains one journey
  bin_no = int((range_rush_morning[1] - range_rush_morning[0])/np.diff(rush_morning_arrivals).min())
  counts, bins, bars = plt.hist(
      np.random.uniform(low=range_rush_morning[0], high=range_rush_morning[1],
                        size=passenger_n),
      bins = bin_no)
  plt.title("Orignial histograms generated for different parts of different days")
  
  # transform counts into frequencies multiplied by percentage of morning travels
  counts = counts / ( passenger_n  * len(rush_morning_arrivals)) * bin_no * rush_morning_per # considering empty bins with no trains
 
  journey_freq[day] = update_journey_freq_day(bins, rush_morning_arrivals, train_route_time_zip, journey_freq[day])

#Repeat for night rush hours
range_rush_night = (18, 21)
rush_night_arrivals = arrival_times_in_range(range_rush_night, arrival_times)

for day in range(len(date_list)):
  #skip weekends!
  if date_list[day].weekday() >= 5:
    continue
# make each day unique by setting a different seed
  np.random.seed(2022+day)
  # number of bins, such that each bin only contains one journey
  bin_no = int((range_rush_night[1] - range_rush_night[0])/np.diff(rush_night_arrivals).min())
  counts, bins, bars = plt.hist(
      np.random.uniform(low=range_rush_night[0], high=range_rush_night[1],
                        size=passenger_n),
      bins = bin_no)
  
  
  # transform counts into frequencies multiplied by percentage of night travels
  counts = counts / ( passenger_n  * len(rush_night_arrivals)) * bin_no * rush_night_per # considering empty bins with no trains
 
  journey_freq[day] = update_journey_freq_day(bins, rush_night_arrivals, train_route_time_zip, journey_freq[day])





# Now we add a uniform distribution to the frequency of all journeys throughout the day

#added .001 to include first and last trains
t_first = min(arrival_times) - .001
t_last = max(arrival_times) + .001

# transform counts into frequencies multiplied by remaining percentage of travels
journey_freq_sums = [sum(sublist) for sublist in journey_freq]
for day in range(len(date_list)):

  np.random.seed(2022+day)
  #if weekend, reduce the number of passengers 
  if date_list[day].weekday() >= 5:
    passenger_no = int(passenger_n * (weekend_per + random.uniform(0, .05)))
  else:
    passenger_no = passenger_n
  # number of bins, such that each bin only contains one journey
  bin_no = int((t_last - t_first)/np.diff(arrival_times).min())
  counts, bins, bars = plt.hist(
      np.random.uniform(low=t_first, high=t_last,
                        size=passenger_no),
      bins = bin_no)
  

  counts = counts / (passenger_no  * len(arrival_times)) * bin_no * (1 - journey_freq_sums[day]) # considering empty bins with no trains
  journey_freq[day] = update_journey_freq_day(bins, arrival_times, train_route_time_zip, journey_freq[day])

# normalize joureny_freq for each day
journey_freq_sums = [sum(sublist) for sublist in journey_freq]
for day in range(len(date_list)):
  journey_freq[day] /= journey_freq_sums[day] # <----------------------ERROR HERE?? divide by zero?
  
# multiply by the number of passengers and transform to integers
journey_passenger_n = [int(x * passenger_n) for day_freq in journey_freq for x in day_freq]

# trim the number of passengers per journey accordingly
journey_passenger_n = [x if x < max_capacity else max_capacity for x in journey_passenger_n]

#create one instance of the journeys for each passenger
passenger_journey = []
journey_dates = []
for day in range(len(date_list)):
  date = str(date_list[day].year) + '-' + str(date_list[day].month) + '-' + str(date_list[day].day)
  for journey_i in range(len(train_route_time_zip)):
    passenger_journey.append([train_route_time_zip[journey_i]] *
                             journey_passenger_n[day*len(train_route_time_zip)+journey_i])
    journey_dates.append([date for _ in range(journey_passenger_n[day*len(train_route_time_zip)+journey_i])])
# convert list of lists into a flat list
passenger_journey = [p for sublist in passenger_journey for p in sublist]
journey_dates = [d for sublist in journey_dates for d in sublist]
#generate ids for passengers; used a large range to create unique ids 
passenger_ids = list(np.random.randint(low=10**len(str(passenger_n * 7)), 
                                       high=10**(len(str(passenger_n * 7))+1),
                                       size=len(passenger_journey)))
#transform integers to strings
passenger_ids = ['p'+str(x) for x in passenger_ids]

# create a dataframe!
train_passenger_df = pd.DataFrame(passenger_journey,
                                  columns=['train_id', 'route', 'arrival_time'])
# add a column for passenger ids
train_passenger_df['passenger_id'] = passenger_ids
train_passenger_df['date'] = journey_dates
# convert arrival time to hour: minute
train_passenger_df['arrival_time'] = train_passenger_df['arrival_time'].astype('int').astype('str') + ':' + ((train_passenger_df['arrival_time'] % 1)*60).astype('str').str[0:2]
# make the correct format for some of the times in 'arrival_time' column
train_passenger_df['arrival_time'] = [time[0:3] + '0' + time[-2] if time[-1] == '.' else time for time in train_passenger_df['arrival_time']]
train_passenger_df['arrival_time'] = ['0' + time[:] if len(time) == 4 else time for time in train_passenger_df['arrival_time']]

# bar plot journey-wise for the number of passengers
(train_passenger_df.groupby('arrival_time').route.value_counts()
   .unstack().plot.bar(width=1, stacked=True))

plt.title("Number of passengers in each journey in a week")
plt.show()

#add shuffle when exporting the data - why make things transparent, eh?
train_passenger_df.sample(frac = 1).to_csv('train_data.csv')