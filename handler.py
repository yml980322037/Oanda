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
    # Change for DST
    def get_latest_rate(self, ticker, granularity='M10', n=10):
        time = datetime.utcnow() + timedelta(hours = 1)
        df = an.average_dataframe(an.selectlast(ticker, granularity, datetime.utcnow() + timedelta(hours = 1), n))
        ev = event.Event('tick', time)
        ev.ticker = ticker
        ev.price = an.get_current_rate(ticker)
        ev.df = df
        ev.spread = an.get_spread(ticker)
        return ev

    def get_single_rate(self, ticker, granularity='M10', n=10):
        datetime_object = datetime.strptime("04/07/17 09:14", "%d/%m/%y %H:%M")
        df = an.average_dataframe(an.selectlast(ticker, granularity, datetime_object, n))
        ev = event.Event('tick', datetime.strptime("03/07/17 21:31", "%d/%m/%y %H:%M"))
        ev.price = {'bid' : df.iloc[-1]['close'] + 0.0001, 'ask' : df.iloc[-1]['close'] - 0.0001}
        ev.df = df
        ev.spread = 1.2
        return ev


class HistoricalDataHandler:
    
    #Initialise row variable for iteration through dataframe
    def __init__(self, ticker, granularity, start, end):
        self.ticker = ticker
        self.granularity = granularity
        self.start = start
        self.end = end
        self.get_data()


    # Load handler with historical data - change to take granularity as input
    def get_data(self):
        df = an.average_dataframe(an.selectdates(self.ticker, self.granularity, self.start, self.end))
        df_full = an.dataframe(an.selectdates(self.ticker, self.granularity, self.start, self.end))
        self.df = df.set_index('time')
        self.df_full = df_full.set_index('time')
        self.rownum = 0


    def push_next_ma_bar_1m(self, gap=4200, open_position = False):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('10Min', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.ticker = self.ticker
        ev.price = {'ask': self.df_full.iloc[lastrow]['closeAsk'], 'bid': self.df_full.iloc[lastrow]['closeBid']}
        ev.spread = round(an.pip_difference(self.df_full.iloc[lastrow]['closeAsk'], self.df_full.iloc[lastrow]['closeBid']), 1)
        self.rownum +=1
        return ev

    def push_next_ma_bar_15m(self, gap=1100, open_position = False):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('15Min', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.ticker = self.ticker
        ev.price = {'ask': self.df_full.iloc[lastrow]['closeAsk'], 'bid': self.df_full.iloc[lastrow]['closeBid']}
        ev.spread = round(an.pip_difference(self.df_full.iloc[lastrow]['closeAsk'], self.df_full.iloc[lastrow]['closeBid']), 1)
        self.rownum +=1
        return ev


    def push_next_ma_bar_1h(self, gap=3000, open_position = False):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('1H', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.ticker = self.ticker
        ev.price = {'ask': self.df_full.iloc[lastrow]['closeAsk'], 'bid': self.df_full.iloc[lastrow]['closeBid']}
        ev.spread = round(an.pip_difference(self.df_full.iloc[lastrow]['closeAsk'], self.df_full.iloc[lastrow]['closeBid']), 1)
        self.rownum +=1
        return ev










