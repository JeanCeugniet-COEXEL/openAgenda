from datetime import datetime, timezone
from time import perf_counter 
import json, os, uuid, math

perf_timers = {}

"""
Start perf timer
"""
def perf_timer_start():
    start_time = perf_counter()
    timer_id = uuid.uuid4()
    perf_timers[timer_id] = {"start": start_time}

    return timer_id

"""
Stop perf timer
"""
def perf_timer_stop(timer_id):
    stop_time = perf_counter()
    timer = perf_timers[timer_id]
    start_time = timer["start"]
    duration = stop_time - start_time
    timer.update({
        "stop": stop_time,
        "duration": duration
    })
    duration_h = math.floor(duration / 3_600)
    duration-= (duration_h * 3_600)
    duration_mn = math.floor(duration / 60)
    duration-= (duration_mn * 60)
    duration_str = ""
    if duration_h:
        duration_str+= f"{duration_h}h "
    if duration_mn:
        duration_str+= f"{duration_mn}mn "
    duration_str+= f"{duration:.2f}s"
    timer.update({"duration_str": duration_str})
    perf_timers[timer_id] = timer

    return timer


"""
Get fomatted datetime for datetime info in results
"""
def formatted_datetime_for_log():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  

"""
Get fomatted datetime for duplicate file renaming
"""
def formatted_datetime_for_filename():
    return datetime.now().strftime("%Y%m-%d-%H%M%S")

def timestamp():
    """
    Get current timestamp in seconds
    """
    return int(datetime.now().timestamp())

"""
Equivalent to php array_chunk
"""
def array_chunk(arr, chunk_size):
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]


def get_current_utc_datetime():
    current_utc_time = datetime.now(timezone.utc)
    formatted_utc_time = current_utc_time.strftime('%Y-%m-%d %H:%M:%S %z')

    return formatted_utc_time

def format_datetime(obj):
    return str(obj)

def log_queries(log_file, queries_list):
    existing_list = []
    if os.path.exists(log_file):
        with open(log_file, "r") as file_in:
            existing_list = json.load(file_in)
    existing_list+= queries_list
    with open(log_file, "w") as file_out:
        file_out.write(json.dumps(existing_list))

def main():
    return None

if __name__ == "__main__":
    main()