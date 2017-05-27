from pandas import Series, DataFrame
import config
import event
import analysis as an
import mysql.connector
from datetime import datetime


class DataHandler:
    
    # Pull and return latest rate (with Dataframe of N previous bars)
    # Add error check for time on df vs current time
    def get_latest_rate(self, granularity='M15', n=10):
        df = an.average_dataframe(an.selectlast(granularity, datetime.utcnow(), n))
        ev = event.event('tick')
        ev.df = df
        ev.spread = an.get_spread('USD_JPY')
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

