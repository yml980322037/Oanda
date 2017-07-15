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
    def __init__(self, ticker, start, end):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.get_data()


    # Load handler with historical data
    def get_data(self):
        df = an.average_dataframe(an.selectdates(self.ticker, 'S5', self.start, self.end))
        self.df = df.set_index('time')
        self.rownum = 0


    #return next section of df   
    def push_next_mr_bar(self, gap=2500):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('10Min', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.ticker = self.ticker
        sqlrow = an.selectrow('GBP_USD', 'S5', self.df.index[lastrow])
        ev.price = {'ask': sqlrow[2], 'bid': sqlrow[6]}
        ev.spread = round((sqlrow[2] - sqlrow[6]) * 10000, 1)
        self.rownum +=1
        return ev


    def push_next_ma_bar(self, gap=5500, open_position = False):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('10Min', how=ohlc_dict).dropna(how='any')
        df_lt = self.df[self.rownum:lastrow].resample('30Min', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.df_lt = df_lt
        ev.ticker = self.ticker
        sqlrow = an.selectrow(self.ticker, 'S5', self.df.index[lastrow])
        ev.price = {'ask': sqlrow[2], 'bid': sqlrow[6]}
        ev.spread = round((sqlrow[2] - sqlrow[6]) * 10000, 1)
        self.rownum +=1
        if open_position == True:
            ev.open_position = True
        else:
            open_position = False
        return ev

    def push_next_ma_bar_st(self, gap=3600, open_position = False):
        lastrow = self.rownum + gap
        ohlc_dict = {'open':'first', 'high':'max', 'low':'min', 'close': 'last'}
        df_min = self.df[self.rownum:lastrow].resample('5Min', how=ohlc_dict).dropna(how='any')
        df_lt = self.df[self.rownum:lastrow].resample('15Min', how=ohlc_dict).dropna(how='any')
        ev = event.Event('tick', self.df.index[lastrow])
        ev.df = df_min
        ev.df_lt = df_lt
        ev.ticker = self.ticker
        sqlrow = an.selectrow(self.ticker, 'S5', self.df.index[lastrow])
        ev.price = {'ask': sqlrow[2], 'bid': sqlrow[6]}
        ev.spread = round((sqlrow[2] - sqlrow[6]) * 10000, 1)
        self.rownum +=1
        if open_position == True:
            ev.open_position = True
        else:
            open_position = False
        return ev











