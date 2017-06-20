from pandas import Series, DataFrame
import config
import event
import analysis as an
import mysql.connector
from datetime import datetime
from datetime import timedelta

# Needs changing for DST

class DataHandler:
    
    # Pull and return latest rate (with Dataframe of N previous bars)
    # Add error check for time on df vs current time
    # Change for DST
    def get_latest_rate(self, granularity='M15', n=10):
        time = datetime.utcnow() + timedelta(hours = 1)
        df = an.average_dataframe(an.selectlast(granularity, datetime.utcnow() + timedelta(hours = 1), n))
        ev = event.Event('tick', time)
        ev.price = an.get_current_rate('USD_JPY')
        ev.df = df
        ev.spread = an.get_spread('USD_JPY')
        return ev

    def get_single_rate(self, granularity='M15', n=10):
        datetime_object = datetime.strptime("14/06/17 23:41", "%d/%m/%y %H:%M")
        df = an.average_dataframe(an.selectlast(granularity, datetime_object, n))
        ev = event.Event('tick', datetime.strptime("30/05/17 01:02", "%d/%m/%y %H:%M"))
        ev.price = {'bid' : df.iloc[-1]['close'] + 0.01, 'ask' : df.iloc[-1]['close'] - 0.01}
        ev.df = df
        ev.spread = 1.2
        return ev



class HistoricalDataHandler:
    
    #Initialise row variable for iteration through dataframe
    #int row = 0

    # Load handler with historical data
    def get_data(self, granularity='M15', n=10):
        pass

    #push next section of dataframe to queue as tick event   
    def push_next_bar():
        pass

