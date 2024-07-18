import time
import pandas as pd
from celery import group
from celery_app import calculate_power_to_weight

def auto_mpg_data_analysis_without_using_celery():

    # make an array of column names and use it to map the columns while reading the data into memory.
    column_names = ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year", "origin", "car_name"]

    # reading and preprocessing of the data. Data cleaning: Replace missing values(?) with NaN using na_values.
    df = pd.read_csv('/Users/sarthakkumar/Downloads/mechademy/auto+mpg/auto-mpg.data', delim_whitespace=True, names=column_names,  na_values = "?")

    # Dropping the rows with NaN value
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # storing the current time as start time 
    start_time = time.time()

    # create a list to store the calculated ratios for all the rows.
    tasks = []

    for index, row in df.iterrows():
        weight = row['weight']
        horsepower = row['horsepower']

        # Calculate the ratio for the current row/task
        result = calculate_power_to_weight(weight, horsepower)

        # Append the result to the tasks list.
        tasks.append((index,result))
    
    # iterate through tasks to update the DataFrame with the calculated power-to-weight ratios.
    for index, result in tasks:
        df.at[index, 'power_to_weight_ratio'] = result

     # storing the current time as end time 
    end_time = time.time()

    # Save the updated DataFrame to a new CSV file
    df.to_csv('auto_mpg_with_power_to_weight_ratio.csv', index=False)

    # calculating the total time taken
    print(("total time taken without using celery: {} seconds".format(end_time-start_time)))


def auto_mpg_data_analysis_using_celery():

    # make an array of column names and use it to map the columns while reading the data into memory.
    column_names = ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year", "origin", "car_name"]

    # reading and preprocessing of the data. Data cleaning: Replace missing values(?) with NaN using na_values.
    df = pd.read_csv('/Users/sarthakkumar/Downloads/mechademy/auto+mpg/auto-mpg.data', delim_whitespace=True, names=column_names,  na_values = "?")

    # Dropping the rows with NaN value
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # storing the current time as start time 
    start_time = time.time()

    # create a list to store the signature for all the rows.
    tasks = []

    # iterate the rows of the DataFrame
    for index, row in df.iterrows():
        weight = row['weight']
        horsepower = row['horsepower']
        
        # Create the signature for the current row/task
        result = calculate_power_to_weight.s(weight, horsepower)

        # Append each task to the tasks list.
        tasks.append(result)

    # Create a group of tasks (job) using group(tasks). This groups all the individual tasks together.
    job = group(tasks)
    
    # Apply the group asynchronously using job.apply_async(), which starts the execution of all tasks in parallel.
    result = job.apply_async()
    
    # retrieve the results of all tasks executed within the group. This waits until all tasks are completed and gathers their results.
    power_to_weight_ratios = result.get()

    # iterate through power_to_weight_ratios and update the DataFrame with the calculated power-to-weight ratios
    for index, result in enumerate(power_to_weight_ratios):
        df.at[index, 'power_to_weight_ratio'] = result

    # storing the current time as end time 
    end_time = time.time()
    
    # To directly add the column power_to_weight_ratio in the DataFrame .
    # df['power_to_weight_ratio'] = power_to_weight_ratios
    
    # Save the updated DataFrame to a new CSV file
    df.to_csv('auto_mpg_with_power_to_weight_ratio.csv', index=False)

    # calculating the total time taken
    print(("total time taken using celery: {} seconds".format(end_time-start_time)))

#auto_mpg_data_analysis_without_using_celery()
auto_mpg_data_analysis_using_celery()