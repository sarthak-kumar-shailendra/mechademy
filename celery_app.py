import time
from celery import Celery

# Initialize Celery application with the local Redis server as the message broker and the backend.
app = Celery('mechademy', broker='redis://127.0.0.1:6379', backend='redis://127.0.0.1:6379')

# Created a Celery task to calculate the power-to-weight ratio for a given row
@app.task
def calculate_power_to_weight(weight, horsepower):
    #time.sleep(0.01)
    if horsepower == 0.0:  # Handle prevent division by zero
        return float('inf')
    return weight / horsepower

