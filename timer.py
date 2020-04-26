import schedule
import time
from datetime import datetime


def job():
    print(datetime.now())

schedule.every().hour.at(':00').do(job)
schedule.every().hour.at(':05').do(job)
schedule.every().hour.at(':10').do(job)
schedule.every().hour.at(':15').do(job)
schedule.every().hour.at(':20').do(job)
schedule.every().hour.at(':25').do(job)
schedule.every().hour.at(':30').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)