import pandas as pd
import numpy as np

# y = mx + c    where c = initial batch duration
def linear_increase(initial, length): 
    gradient = np.random.uniform(1,1.2)
    durations = [((n*gradient)+initial) for n in range(length)]
    durations = pd.Series(durations).round(decimals = 2)
    return durations

# y = mx^2 + c   where c = initial batch duration
def quadratic_increase(initial, length): 
    gradient = np.random.uniform(0.01,0.07)
    durations = [(((n**2)*gradient)+initial) for n in range(length)]
    durations = pd.Series(durations).round(decimals = 2)
    return durations

# y = y-1*percentage    where y1 = initial batch duration
def percentage_increase(initial, length):
    percentage_increase = 1.005
    durations = [((percentage_increase**n)*initial) for n in range(length)]
    durations = pd.Series(durations).round(decimals = 2)
    return durations 


