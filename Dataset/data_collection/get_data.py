import csv
import datetime as dt
import json
import os
import statistics
import time

# third-party imports
import numpy as np
import pandas as pd
import requests

# customisations - ensure tables show all columns
pd.set_option("display.max_columns", 100)

print("checkpoint 1")
def get_request(url, parameters=None, max_retries=5):
    """Send a GET request and return JSON, retrying invalid responses."""

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url=url,
                params=parameters,
                timeout=30
            )

            response.raise_for_status()

            if not response.text.strip():
                raise ValueError("Empty response")

            return response.json()

        except (
            requests.RequestException,
            requests.exceptions.JSONDecodeError,
            ValueError
        ) as error:
            print(
                f"\nRequest failed: {error} "
                f"(attempt {attempt}/{max_retries})"
            )

            if attempt < max_retries:
                wait = attempt * 10
                print(f"Waiting {wait} seconds...")
                time.sleep(wait)

    return None 


url = "https://steamspy.com/api.php"
parameters = {"request": "all"}


# request 'all' from steam spy and parse into dataframe
json_data = get_request(url, parameters=parameters)
steam_spy_all = pd.DataFrame.from_dict(json_data, orient='index')

print("checkpoint 2")

# generate sorted app_list from steamspy data
app_list = steam_spy_all[['appid', 'name']].sort_values('appid').reset_index(drop=True)

# export 
os.makedirs("../data/download", exist_ok=True)

app_list.to_csv('../data/download/app_list.csv', index=False)

#  read from stored csv 
app_list = pd.read_csv('../data/download/app_list.csv')

print("checkpoint 3")
print(os.getcwd())

# display first few rows
print(app_list.head())

def get_app_data(start, stop, parser, pause):
    """Return list of app data generated from parser.
    
    parser : function to handle request
    """
    app_data = []
    
    # iterate through each row of app_list, confined by start and stop
    for index, row in app_list[start:stop].iterrows():
        print('Current index: {}'.format(index), end='\r')
        
        appid = row['appid']
        name = row['name']

        # retrive app data for a row, handled by supplied parser, and append to list
        data = parser(appid, name)

        if data is not None:
            app_data.append(data)
        time.sleep(pause) # prevent overloading api with requests
    
    return app_data


def process_batches(parser, app_list, download_path, data_filename, index_filename,
                    columns, begin=0, end=-1, batchsize=100, pause=1):
    """Process app data in batches, writing directly to file.
    
    parser : custom function to format request
    app_list : dataframe of appid and name
    download_path : path to store data
    data_filename : filename to save app data
    index_filename : filename to store highest index written
    columns : column names for file
    
    Keyword arguments:
    
    begin : starting index (get from index_filename, default 0)
    end : index to finish (defaults to end of app_list)
    batchsize : number of apps to write in each batch (default 100)
    pause : time to wait after each api request (defualt 1)
    
    returns: none
    """
    print('Starting at index {}:\n'.format(begin))
    
    # by default, process all apps in app_list
    if end == -1:
        end = len(app_list) + 1
    
    # generate array of batch begin and end points
    batches = np.arange(begin, end, batchsize)
    batches = np.append(batches, end)
    
    apps_written = 0
    batch_times = []
    
    for i in range(len(batches) - 1):
        start_time = time.time()
        
        start = batches[i]
        stop = batches[i+1]
        
        app_data = get_app_data(start, stop, parser, pause)
        
        rel_path = os.path.join(download_path, data_filename)
        
        # writing app data to file
        with open(rel_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            
            for j in range(3,0,-1):
                print("\rAbout to write data, don't stop script! ({})".format(j), end='')
                time.sleep(0.5)
            
            writer.writerows(app_data)
            print('\rExported lines {}-{} to {}.'.format(start, stop-1, data_filename), end=' ')
            
        apps_written += len(app_data)
        
        idx_path = os.path.join(download_path, index_filename)
        
        # writing last index to file
        with open(idx_path, 'w') as f:
            index = stop
            print(index, file=f)
            
        # logging time taken
        end_time = time.time()
        time_taken = end_time - start_time
        
        batch_times.append(time_taken)
        mean_time = statistics.mean(batch_times)
        
        est_remaining = (len(batches) - i - 2) * mean_time
        
        remaining_td = dt.timedelta(seconds=round(est_remaining))
        time_td = dt.timedelta(seconds=round(time_taken))
        mean_td = dt.timedelta(seconds=round(mean_time))
        
        print('Batch {} time: {} (avg: {}, remaining: {})'.format(i, time_td, mean_td, remaining_td))
            
    print('\nProcessing batches complete. {} apps written'.format(apps_written))

def reset_index(download_path, index_filename):
    """Reset index in file to 0."""
    rel_path = os.path.join(download_path, index_filename)
    
    with open(rel_path, 'w') as f:
        print(0, file=f)
        

def get_index(download_path, index_filename):
    """Retrieve index from file, returning 0 if file not found."""
    try:
        rel_path = os.path.join(download_path, index_filename)

        with open(rel_path, 'r') as f:
            index = int(f.readline())
    
    except FileNotFoundError:
        index = 0
        
    return index


def prepare_data_file(download_path, filename, index, columns):
    """Create file and write headers if index is 0."""
    if index == 0:
        rel_path = os.path.join(download_path, filename)

        with open(rel_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

def parse_steamspy_request(appid, name):
    """Parser to handle SteamSpy API data."""

    url = "https://steamspy.com/api.php"
    parameters = {
        "request": "appdetails",
        "appid": appid
    }

    json_data = get_request(url, parameters)

    if json_data is None:
        print(f"Skipping app {appid}: {name}")
        return None

    return json_data
# set files and columns
download_path = '../data/download'
steamspy_data = 'steamspy_data.csv'
steamspy_index = 'steamspy_index.txt'

steamspy_columns = [
    'appid', 'name', 'developer', 'publisher', 'score_rank', 'positive',
    'negative', 'userscore', 'owners', 'average_forever', 'average_2weeks',
    'median_forever', 'median_2weeks', 'price', 'initialprice', 'discount',
    'languages', 'genre', 'ccu', 'tags'
]

#reset_index(download_path, steamspy_index)
index = get_index(download_path, steamspy_index)

# Wipe data file if index is 0
prepare_data_file(download_path, steamspy_data, index, steamspy_columns)

process_batches(
    parser=parse_steamspy_request,
    app_list=app_list,
    download_path=download_path, 
    data_filename=steamspy_data,
    index_filename=steamspy_index,
    columns=steamspy_columns,
    begin=0,
    #end=20,
    #batchsize=5,
    pause=0.3
)
pd.read_csv('../data/download/steamspy_data.csv').head()