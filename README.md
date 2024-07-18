Auto MPG Data Analysis with Celery

## Objective
The objective of this task is to demonstrate the ability to work with the Auto MPG dataset, perform data analysis, and use Celery to handle parallel processing tasks. We aim to calculate the power-to-weight ratio for each car using Celery for parallel processing.

1) Set up the environment with the necessary packages.

    A. Install the required packages: pip3 install pandas celery redis.
   
    B. Set up a Redis server locally to be used as the message broker for Celery: One can go to redis.io to check the steps required to install redis in their local machine. For convenience you can also use Docker to start a redis server using the commmand 
    docker run -d -p 6379:6379 redis

       Link - https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-mac-os/ 

3) Load and preprocess the Auto MPG dataset.

    A. We can load the Auto MPG dataset from the provided URL and preprocess it by removing rows with missing values(?). First, we replace missing values(?) with NaN using na_values and then we drop the rows with NaN value and reset the dataframe index.
    
    Dataset URL - https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data

4) Setting Up Celery for Parallel Processing & Define a Celery task to calculate the power-to-weight ratio.

    A. Setting Up Celery Instance and defining the task
        We import Celery and define the task in celery_app.py, ensuring it's configured to use Redis as both the broker and backend.
        Once the Celery instance is created we create a Celery task to calculate the power-to-weight ratio for a given row using the formula:
        
        Power-to-Weight Ratio= Weight / Horsepower
    
    B. Grouping Tasks and parallel execution
        After configuring the celery, we create an empty list to store the parallel tasks and the we iterate through each row of the DataFrame to create tasks (calculate_power_to_weight.s(...)) using the .s() method, which creates a signature for the task. We append each task to the tasks list.
        
   Then we create a group of tasks (job) using group(tasks). This groups all the individual tasks together.
   Then we apply the group asynchronously using job.apply_async(), which starts the execution of all tasks in parallel.

6) Combine Results and update the dataframe:

    We collect the results from the Celery tasks using result.get(). This waits until all tasks are completed and gathers their results. Then we can iterate through power_to_weight_ratios to print or process each result as needed. 
    
    We can directly add the column 'power_to_weight_ratio' in the DataFrame using

       df['power_to_weight_ratio'] = power_to_weight_ratios
    
    To Save the updated DataFrame to a new CSV file we can run the following command

       df.to_csv('auto_mpg_with_power_to_weight_ratio.csv', index=False)

8) Running the code
   
    A. Run the redis server using the command "redis-server" in the terminal.
   
    B. Navigate to the directory containing the script and start a Celery worker by running:

       celery -A celery_app  worker --loglevel=info
    
    The breakdown of the above command 
    celery: This is the command-line interface for Celery. It allows you to start workers, manage tasks, inspect tasks, and more.
    
    -A celery_app: The -A option specifies the Celery application instance to use. In this case, celery_app is the name of your Celery application instance. It is typically the module where your Celery app is defined.
    
    worker: This part of the command tells Celery to start a worker process. A worker is a process that executes tasks defined in your Celery application. Workers listen for tasks on the message broker and execute them when they are received.
    
    --loglevel=info: This option sets the logging level for the worker process. The info level provides a moderate amount of log output, which includes basic information about task processing, worker status, and any errors or warnings.

    C. Open another terminal, navigate to the directory containing the script, and run
    
            python3 mechademy.py

## Thought Process, Decision Making and Challenges Faced and how I overcame them

1. Setting Up the Environment: The first challenge/step was to ensure that all necessary packages and dependencies were installed and also that the local redis server was running properly. To test whether Redis is working properly or not I typed the following command in the terminal. 

        redis-cli ping 
2. Handling Missing Values: The next challenge was to ensure that the dataset is clean and free of missing values to prevent errors during computation. Missing values in the horsepower column were handled by dropping rows with missing data.

3. Handling ZeroDivisionError: During the Celery task creation to calculate the power-to-weight ratio for each row I handled the case where horsepower is zero to avoid division by zero errors.

4. Celery Task: Since we have to calculate the power-to-weight for each of the rows it is essential to set up the Celery worker that can handle multiple tasks concurrently and leverage the power of multi-core processors to speed up processing. To create tasks for all the rows, we used .s() signature function and stored it in a list for parallel processing.

5. Parallel Processing & Resource Management: By leveraging Celery's group functionality and apply_async(), we efficiently handle the parallel execution of tasks. We can monitor system performance and adjusted the number of concurrent workers as needed. By default, Celery will create as many worker processes as the number of CPU cores available on the machine. This can be controlled by adding the --concurrency option while starting the worker.

6. Updating dataframe: Resetting the dataframe index helped us in inserting the collected results at their correct index in the dataFrame .

7. Testing and Validation: We tested the code by running it on the provided dataset and verifying that the output CSV file contains the calculated power-to-weight ratios for each car.

I am also measuring the start time and end time using time module to calculate the total time taken to process the tasks.
Also, I wrote a similar function for calculating the ratios for all the rows in a synchronous manner without using celery.
The results were 

    total time taken without using celery: 0.012104272842407227 seconds
    total time taken using celery: 0.7963268756866455 seconds

<img width="661" alt="Screenshot 2024-07-19 at 3 30 35 AM" src="https://github.com/user-attachments/assets/6cd53186-1182-4a33-b2ac-86056ff8ca7b">


This was because our celery task was a lightweight task and due to the lack of overhead from inter-process communication. There is some overhead associated with task queuing, dispatching, and collecting results, which can make it slower for very small or simple tasks.

The performance comparison between Celery and synchronous processing depends on various factors including the number of CPU cores, the efficiency of the Celery worker setup, the overhead of inter-process communication, and the nature of the task itself and dataset size.

However for large datasets or more computationally intensive tasks, Celery can leverage multiple workers and parallelize the workload, potentially speeding up the processing. 

To give a concrete comparison, I suspended execution for 0.01 seconds using time.sleep(0.01) in the celery task.
This time the results were 

    total time taken without using celery: 4.8555028438568115 seconds
    total time taken using celery: 0.7521679401397705 seconds

<img width="660" alt="Screenshot 2024-07-19 at 3 38 25 AM" src="https://github.com/user-attachments/assets/5e06ebe2-53d7-4658-a9ad-4f59d61c7b12">

When we were not using celery and doing synchronous operation for all the 392 ~ 400 rows there was a wait time of 0.01 seconds. 
400*0.01= 4 seconds 
So, the execution without celery takes around 4.8 seconds.
But since we are doing parallel processing in celery, suspending the execution for 0.01 seconds didn't have a greater effect. 

Once the processing is done by the worker processes, the results get stored in the redis. We can see that all the 392 results are present in the redis.

<img width="642" alt="Screenshot 2024-07-19 at 3 55 50 AM" src="https://github.com/user-attachments/assets/d95fb3ce-89fa-41eb-803c-91c7e28cdefd">
