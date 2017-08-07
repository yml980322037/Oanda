from pandas import Series, DataFrame
import config
import event
import analysis as an
import mysql.connector
from datetime import datetime, timedelta
from dateutil.rrule import rrule, HOURLY, SECONDLY

# Needs changing for DST

class DataHandler:
    # Pull and return latest rate (with Dataframe of N previous bars)
    # Add error check for time on df vs current time
    def get_latest_rate(self, ticker, granularity='M10', n=10):
        time = datetime.utcnow() + timedelta(hours = 1)
        df = an.average_dataframe(an.selectlast(ticker, granularity, datetime.utcnow() + timedelta(hours = 1), n))
        ev = event.Event('tick', time)
        ev.ticker = ticker
        ev.price = an.get_current_rate(ticker)
        ev.df = df
        ev.spread = an.get_spread(ticker)
        return ev


class HistoricalDataHandler:
    
    #Initialise row variable for iteration through dataframe
    def __init__(self, ticker, granularity, start, end):
        self.ticker = ticker
        self.granularity = granularity
        self.start = start
        self.end = end
        self.get_data()
        self.ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}


    # Load handler with historical data - change to take granularity as input
    def get_data(self):
        df = an.average_dataframe(an.selectdates(self.ticker, self.granularity, self.start - timedelta(hours = 100), self.end))
        df_full = an.dataframe(an.selectdates(self.ticker, self.granularity, self.start - timedelta(hours = 100), self.end))
        self.lastrow = df.loc[df['time'] == self.start].index[0]
        self.df = df.set_index('time')
        self.df_full = df_full.set_index('time')


    def push_next_ma_bar_1h(self, gap=1300):
        ev = event.Event('tick', self.df.index[self.lastrow])
        ev.df = self.df[self.lastrow - gap:self.lastrow].resample('1H', how=self.ohlc_dict).dropna(how='any')
        ev.ticker = self.ticker
        ev.price = {'ask': self.df_full.iloc[self.lastrow]['closeAsk'], 'bid': self.df_full.iloc[self.lastrow]['closeBid']}
        ev.spread = round(an.pip_difference(self.df_full.iloc[self.lastrow]['closeAsk'], self.df_full.iloc[self.lastrow]['closeBid']), 1)
        self.lastrow += 1
        return ev










