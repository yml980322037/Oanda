
# coding: utf-8

# In[3]:

from abc import ABCMeta, abstractmethod
from pandas import Series, DataFrame
import config
import mysql.connector
from datetime import datetime


# In[6]:

class DataHandler:
    
    
    def get_latest_data(self, N=1):
        pass
        # Pull and store latest rate (with Dataframe on N number of previous bars)
        
    
    def push_next_bar():
        pass
        # Push Dataframe object to queue


# In[5]:

class HistoricalDataHandler:
    
    # Load handler with historical data
    def get_latest_data(self, N=1):
        pass
        #Pull and store N number of bars or historical data
        
    def push_next_bar():
        pass
        # Push Dataframe & Previous N number of bars to queue

