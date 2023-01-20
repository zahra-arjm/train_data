import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import random
import datetime


df = pd.read_csv("train_data.csv")

#histogram of number of passengers per train
df.groupby(['route','arrival_time','date'])['passenger_id'].count().hist()
plt.title("Number of passengers per trian")
# plt.show()

max_capacity = 500

percent_full = .5
busy_train_percent = .8

joureny_not_full_frequency = (df.groupby(['route','arrival_time','date'])['passenger_id'].count() < (percent_full * max_capacity)).sum() \
/ (df.groupby(['route','arrival_time','date'])['passenger_id'].count() < max_capacity).sum()
print(f"Percent of trains which are {int(percent_full * 100)}% full: {joureny_not_full_frequency: .2f}")
# number of journeys in the data set
journey_no = df.groupby(['route','arrival_time','date']).size().count()
print(f"Total number of journeys: {journey_no}")
average_pass_per_train = int(df.groupby(['route','arrival_time','date'])['passenger_id'].count().mean())
print(f"Average number of passengers per train: {average_pass_per_train}")

# passengers' point of view

#add number of passengers per journey
arrivals = df.groupby(['arrival_time','date'])['passenger_id'].count()
#use this as concordance to add passenger count to original df
df=df.merge(arrivals, on = ['arrival_time', 'date'])
df.drop('Unnamed: 0', axis=1, inplace=True) #don't need this in notebook for some reason
df.columns = ['train_id', 'route', 'arrival_time', 'passenger_id', 'date', 'passenger_count'] 

# frequency of passengers commuting in busy trains:
busy_train_passenger_frequency = np.sum(df['passenger_count']>(busy_train_percent * max_capacity)) / len(df)
print(f"Frequency of passengers commuting in a train more than {int(busy_train_percent * 100)}% full: {busy_train_passenger_frequency: .2f}")