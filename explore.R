library("dplyr")
library("ggplot2")

df <- read.csv('train_data.csv')


#take a look at the first five lines of the data
head(df)

#or this way
str(df)

unique(df$train_id)
unique(df$route)
unique(df$arrival_time)


#since none of the variables alone, show us one specific journey, we need to combine them
journeys <- df %>% 
  group_by(train_id, route, arrival_time, date) %>% 
  summarise(passenger_count = n())
journeys

# size of journeys are 281; let's see if we can remove the train_id from groupping variables
journeys <- df %>%
  group_by(route, arrival_time, date) %>%
  summarise(passenger_count = n())
journeys
#again, we have 281 journeys; it seems we can ignore the train_id for now

#Now, let's look at the distribution of passenger count in each journey
ggplot(journeys, aes(x = passenger_count)) +
  geom_histogram()
# there are a lot of trains which run near empty, and a lot of them which are full
# let's extract some statistics
summary(journeys$passenger_count)
# based on the number of passengers per journey, we can see that the average number 
# of passenger per journey is 214. Given that the maximum number of passengers in a journey
# is 500 (the capacity of a train) and the median of the passenger count is 102,
# more that half of the trains are more than half empty. In fact we can check out
# how many journeys run with less than 250 passengers
sum(journeys$passenger_count < 250)

# 179 trains were less than half empty; what is the frequency of half empty trains?
sum(journeys$passenger_count < 250) / length(journeys$passenger_count)
# 63% ! it seems that the argument of train companies are true. But what about how
# passenger feel? Do passengers have a point when complaining about crowded trains?

#let's add a column to the data frame, showing the number of passenger in the journey
df <- df %>%
  group_by(arrival_time, date) %>%
  mutate(passengerc_count = n())

# let's define a busy train to be 80% full
max_capacity = 500
busy_train_percent = .8

# frequency of passengers commuting with a busy train
sum(df$passengerc_count > busy_train_percent * max_capacity) /
  length(df$passengerc_count)

# 54% of passengers are commuting with busy trains! It seems the commuters also
# have a point!