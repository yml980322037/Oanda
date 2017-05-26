from pandas import Series, DataFrame
import config
import mysql.connector
from datetime import datetime


class DataHandler:
    
    
    def get_latest_data(self, N=1):
        pass
        # Pull and store latest rate (with Dataframe on N number of previous bars)
        
    
    def push_next_bar():
        pass
        # Push Dataframe object to queue



class HistoricalDataHandler:
    
    # Load handler with historical data
    def get_latest_data(self, N=1):
        pass
        #Pull and store N number of bars or historical data
        
    def push_next_bar():
        pass
        # Push Dataframe & Previous N number of bars to queue

