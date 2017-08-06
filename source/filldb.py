import source
from datetime import datetime, timedelta
from dateutil import rrule
import time
import sys

GBP_USD = source.Source('GBP_USD')

# Creates table if not on DB
GBP_USD.create_table('M1')


for i in rrule.rrule(rrule.HOURLY, interval = 83, dtstart=datetime(2017,1,1), until=datetime(2017,8,6)):
    time = datetime.strftime(i, '%Y-%m-%d %H:%M:%S')
    print(time)
    GBP_USD.pull_to_table_by_len(time, 5000, 'M1')