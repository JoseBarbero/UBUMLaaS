import threading
import asyncio
import time
from datetime import datetime, date
import variables as v
import pandas as pd
import os
import numpy as np
import logging
import sys

def os_execute(command):
    os.system(command)


def os_monitor(command, message=""):
    logging.info(message)
    try:
        os.system(command)
    except Exception as e:
        pass

def run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def monitor_clean_csv(path):
    import time
    time.sleep(86400)
    logging.info('Starting Monitor Cleaner')
    try:
        csv_df = pd.read_csv(path)
        csv_clean = csv_df.drop_duplicates(subset=['timestamp'])
        now = datetime.now()
        now = date(now.year, now.month, now.day)
        last_row = None
        for index, row in csv_clean.iterrows():
            time = row.timestamp
            time = date(*np.array(time.split(' ')[0].split('-')).astype(int))
            if (now - time).days > 180:
                last_row = index
            else:
                break
        
        if last_row is not None:
            csv_clean = csv_clean[last_row+1:]

        csv_clean.to_csv(path, index=False)
    except Exception as e:
        pass


def create_monitor():
    """ Start the server monitor threads.
    """
    monitor_event_loop = asyncio.new_event_loop()
    monitor_clean_loop = asyncio.new_event_loop()
    command = "glances --export csv --export-csv-file " + \
        str(os.environ['LIBFOLDER']) + "/glances.csv --time 60 --quiet"
    threading.Thread(target=lambda: run_loop(
        monitor_event_loop)).start()
    threading.Thread(target=lambda: run_loop(
        monitor_clean_loop)).start()
    monitor_event_loop.call_soon_threadsafe(
        lambda: os_monitor(command, f"Executing {command}"))
    monitor_clean_loop.call_soon_threadsafe(
        lambda: monitor_clean_csv(str(os.environ['LIBFOLDER']) + "/glances.csv"))


if __name__ == '__main__':
    create_monitor()