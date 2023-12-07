import pandas as pd
import numpy as np
from datetime import datetime
from increase_functions import linear_increase, quadratic_increase, percentage_increase
from random import random, choice 
from pathlib import Path 
from datetime import date
from datetime import timedelta

## Assigns AWS Instance size to a company based on 
def assign_aws_instance(sales_volume):
    instance_list = ['Small', 'Medium', 'Larg', 'Extra Large']
    #Small Daily Sales Volume
    if sales_volume<5e5:
        return np.random.choice(instance_list, p=[0.65,0.35,0,0])
    #Medium Daily Sales Volume
    elif sales_volume<1.5e6:
        return np.random.choice(instance_list, p=[0,0.8,0.2,0])
    # Large Daily Sales Volume
    elif sales_volume<6e6: 
        return np.random.choice(instance_list, p=[0,0,0.75,0.25])
    #Extra Large Daily Sales Volume
    else: 
        return np.random.choice(instance_list, p=[0,0,0,1])

## Assign a random start date (date of first batch) to each customer
def assign_start_date(start,end, length):
    start_dates = np.random.choice(pd.date_range(start, end), length)
    return start_dates

def assign_average_sale_price(min,max, length): 
    average_sale_price = np.random.randint(min,max,size =length)
    return average_sale_price

def generate_aws_multiplier(AWS_instance):
    multiplier=0
    if AWS_instance == "Extra Large":
        multiplier = 0.05
    elif AWS_instance == "Large":
        multiplier = 0.20
    elif AWS_instance== "Medium":
        multiplier = 0.5
    elif AWS_instance == "Small": 
        multiplier = 0.8
    
    return multiplier

## Apply a randomly selected increase function to generate batch run durations.
def generate_batch_durations(initial, length):
    functions = [linear_increase(initial, length), 
                 quadratic_increase(initial, length), 
                 percentage_increase(initial, length)]
    
    raw_durations = choice(functions)

    # Add noise and also random outliers to the data using normal distribution  
    durations_with_noise = [np.random.normal(np.random.choice([raw_durations[n],raw_durations[n]*np.random.uniform(1.5,4)],p=[0.999,0.001]),raw_durations[n]*0.1,1)[0] for n in range(length)]
    return durations_with_noise

## Generate a new dataframe of batch times for a customer based on:
# 1. AWS Instance  
# 2. Number of transactions  
# 3. Time since first batch run

def create_batch_data(company, start_date, daily_sales, AWS_instance):
    ## Generate dataframe with dates column having row for each batch run date. 
    
    # End Date = today.  Random chance for it to be today -1/2/3/4/5 days (to simulate batch failures in previous days)
    end_date = pd.to_datetime(date.today())- timedelta(days=int(np.random.choice([0,1,2,3,4,5], p=[0.95,0.01,0.01,0.01,0.01,0.01])))

    dates_list = pd.date_range(start=start_date, end = end_date, freq= 'D')
    batch_data = pd.DataFrame(dates_list, columns=['Batch_Date'], index=None)
    batch_data['Company'] = company

    # Calculate initial batch run duration 
    initial_duration = (daily_sales*0.0003) * generate_aws_multiplier(AWS_instance)

    # Calculate remaining batch run durations
    batch_data['Duration'] = generate_batch_durations(initial_duration,len(batch_data))

    return batch_data

## Read in raw data from Scraper
data_path = Path('Data/')
customers = pd.read_csv(data_path / '01_raw.csv')

## For each customer assign further specifications: StartDate, average sale price, average daily sales, AWS Instance.
# Assign start date to each customer
customers['start_date'] = assign_start_date('2022-10-01','2023-02-01',len(customers))

# Assign avg price per sale of each customer
customers['average_sale_price'] = assign_average_sale_price(5,1000, len(customers))

#Calculate avg number of daily sales per customer
customers['daily_sales'] = (customers['revenueUSD']/customers['average_sale_price'] ) / 365

# Assign AWS Instance to each customer
customers['AWS_instance'] = customers['daily_sales'].apply(lambda x: assign_aws_instance(x))

# Save finalised customers dataframe to csv
customers.to_csv(data_path / '02_intermediate.csv', index = False)


## Loop through each row (company) in the companies dataframe and produce batch data
# Save each companies batch dataframe in a dictionary using Company name as key
batch_frames = {}

for row in customers.itertuples():
    company = row[1]
    start_date = row[3]
    daily_sales = row[5]
    aws_instance = row[6]
    batch_data = create_batch_data(company, start_date, daily_sales, aws_instance)
    batch_frames[company] = batch_data

## Combine all companies batch data into 1 dataset (03_final.csv)
batch_data  = pd.concat(batch_frames)
batch_data.to_csv(data_path / '03_final.csv', index=  False)
