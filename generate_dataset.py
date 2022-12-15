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
# keep all the times in one list
hours = []
# generate uniformly distributed hours for each route throughout the day with random start and end (from 6 am to 11 pm plus minus 1 hour)
for route_i in range(len(routes)):
  route_i_times = list(np.linspace(start=6+((np.random.rand())*2 - 1), stop=(23+((np.random.rand())*2 - 1)), num=journey_per_route_n[route_i]))
  journey_times.append(route_i_times)
  hours.extend(route_i_times)
#transform to numpy array and sort
hours = np.array(hours)
hours.sort()

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
rush_nights_per = .3
# proportion of passengers in weekday compared to weekdays
weekend_per = .25
# build a histogram with a uniform distribution. Bin width is equal to minimum of the difference between train times

# rush hour starts at
rush_m_start = 7
# rush hour ends at
rush_m_end = 10
# find the min difference between train arrivals in the morning rush hours
rush_morning = hours[np.where(np.logical_and(hours>=rush_m_start, hours<=rush_m_end))]
min_rush_m = np.diff(rush_morning).min()

# empty list of frequencies for all journeys
journey_freq = [[0] * len(train_route_time_zip) for _ in range(len(date_list))]

for day in range(len(date_list)):
  #skip weekends!
  if date_list[day].weekday() >= 5:
    continue
# make each day unique by setting a different seed
  np.random.seed(2022+day)
  # number of bins, such that each bin only contains one journey
  bin_no = int((rush_m_end - rush_m_start)/min_rush_m)
  counts, bins, bars = plt.hist(
      np.random.uniform(low=rush_m_start, high=rush_m_end,
                        size=passenger_n),
      bins = bin_no)
  
  
  # transform counts into frequencies multiplied by 40 percent morning travels
  counts = counts / ( passenger_n  * len(rush_morning)) * bin_no * rush_morning_per # considering empty bins with no trains
  
  ##assign frequncuies to each journey

  # find train-time which fits within each bin of the histogram
  for bin_i in range(len(bins)-1):
    t_time = rush_morning[np.where(np.logical_and(rush_morning>=bins[bin_i], rush_morning<=bins[bin_i+1]))]
    # find index of the journey in the list of tuples of journeys if t_time is not empty
    if len(t_time):
      t_idx = [idx for idx, tup in enumerate(train_route_time_zip) if tup[2] == t_time]
      # set frequency of the journey to histogram count if t_idx is not empty
      if len(t_idx): 
        journey_freq[day][t_idx[0]] = counts[bin_i]

#Repeat for night rush hours (6-9 pm since it is arrival times)
# build a histogram with a uniform distribution. Bin width is equal to minimum of the difference between train times

# rush hour starts at
rush_n_start = 18
# rush hour ends at
rush_n_end = 21
# find the min difference between train arrivals in the morning rush hours
rush_nights = hours[np.where(np.logical_and(hours>=rush_n_start, hours<=rush_n_end))]
min_rush_n = np.diff(rush_nights).min()

for day in range(len(date_list)):
  #skip weekends!
  if date_list[day].weekday() >= 5:
    continue
  np.random.seed(2022+day)
  # number of bins, such that each bin only contains one journey
  bin_no = int((rush_n_end - rush_n_start)/min_rush_n)
  counts, bins, bars = plt.hist(
      np.random.uniform(low=rush_n_start, high=rush_n_end,
                        size=passenger_n),
      bins = bin_no)
  # transform counts into frequencies multiplied by 30 percent morning travels 
  counts = counts / (passenger_n  * len(rush_nights)) * bin_no * rush_nights_per  # considering empty bins with no trains
  ##assign frequncuies to each journey
  # find train-time which fits within each bin of the histogram
  for bin_i in range(len(bins)-1):
    t_time = rush_nights[np.where(np.logical_and(rush_nights>=bins[bin_i], rush_nights<=bins[bin_i+1]))]
    # find index of the journey in the list of tuples of journeys if t_time is not empty
    if len(t_time):
      t_idx = [idx for idx, tup in enumerate(train_route_time_zip) if tup[2] == t_time]
      # set frequency of the journey to histogram count if t_idx is not empty
    if len(t_idx):   
        journey_freq[day][t_idx[0]] = counts[bin_i]

# Now we add a uniform distribution to the frequency of all journeys throughout the day
# first train arrives at
t_first = min(hours) - .001
# last train arrives at
t_last = max(hours) + .001
# find the min difference between train arrivals
min_t_arrivals = np.diff(hours).min()
# transform counts into frequencies multiplied by remaining percentage of travels
journey_freq_sums = [sum(sublist) for sublist in journey_freq]
for day in range(len(date_list)):

  np.random.seed(2022+day)
  #if weekend, reduce the number of passengers is about 25 percent of normal days
  if date_list[day].weekday() >= 5:
    passenger_no = int(passenger_n * (weekend_per + random.uniform(0, .05)))
  else:
    passenger_no = passenger_n
  # number of bins, such that each bin only contains one journey
  bin_no = int((t_last - t_first)/min_t_arrivals)
  counts, bins, bars = plt.hist(
      np.random.uniform(low=t_first, high=t_last,
                        size=passenger_no),
      bins = bin_no)
  

  counts = counts / (passenger_no  * len(hours)) * bin_no * (1 - journey_freq_sums[day]) # considering empty bins with no trains
  ##assign frequncuies to each journey and transform it into passenger numbers
  # find train-time which fits within each bin of the histogram
  for bin_i in range(len(bins)-1):
    t_time = hours[np.where(np.logical_and(hours>=bins[bin_i], hours<=bins[bin_i+1]))]
    # find index of the journey in the list of tuples of journeys if t_time is not empty
    if len(t_time):
      t_idx = [idx for idx, tup in enumerate(train_route_time_zip) if tup[2] == t_time]
      # print(t_idx)
      # set frequency of the journey to histogram count if t_idx is not empty
      if len(t_idx):
        journey_freq[day][t_idx[0]] += counts[bin_i]

# normalize joureny_freq for each day
journey_freq_sums = [sum(sublist) for sublist in journey_freq]
for day in range(len(date_list)):
  journey_freq[day] /= journey_freq_sums[day]
# multiply by the number of passengers and transform to integers
journey_passenger_n = [int(x * passenger_n) for day_freq in journey_freq for x in day_freq]
# the max capacity of the train
max_capacity = 500
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

train_passenger_df.to_csv('train_data.csv')