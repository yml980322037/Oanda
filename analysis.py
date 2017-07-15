from pandas import Series, DataFrame
import requests
import json
import config
import mysql.connector
from datetime import datetime
from mysql.connector import errorcode
from decimal import Decimal

sql_host = config.sql_host
sql_user = config.sql_user_analysis
sql_password = config.sql_password_analysis

url = config.url
access_token = config.access_token
account_id = config.account_id


# Returns tuple for each sql row.
def selectlast(ticker, granularity, time, rows):
    
    sql = ("SELECT * FROM (SELECT * FROM {} WHERE time <= '{}' "
           "ORDER BY time DESC LIMIT {})a ORDER BY time ASC;".format(granularity, time, rows))
    cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                             host=sql_host, database='{}'.format(ticker))
    cursor = cnx.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()
    return results;

def selectdates(ticker, granularity, start, end):
    
    sql = ("SELECT * FROM {} WHERE time BETWEEN '{}' AND '{}';".format(granularity, start, end))
    cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                             host=sql_host, database='{}'.format(ticker))
    cursor = cnx.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()
    return results;

def selectrow(ticker, granularity, time):
    
    sql = ("SELECT * FROM {} WHERE time = '{}';".format(granularity, time))
    cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                             host=sql_host, database='{}'.format(ticker))
    cursor = cnx.cursor()
    cursor.execute(sql)
    results = cursor.fetchone()
    cursor.close()
    cnx.close()
    return results;


# Create dataframe from sql query result
def dataframe(sqltable):
    names = ['time', 'openAsk', 'closeAsk', 'lowAsk', 'highAsk', 'openBid', 'closeBid', 'lowBid', 'highBid', 'volume']
    df = DataFrame(sqltable, columns = names)
    #df.set_index('time', inplace=True)
    return df


def average_dataframe(sqltable):
    names = ['time', 'openAsk', 'closeAsk', 'lowAsk', 'highAsk', 'openBid', 'closeBid', 'lowBid', 'highBid', 'volume']
    df = DataFrame(sqltable, columns = names)
    df['open'] = df[['openAsk', 'openBid']].mean(axis=1)
    df['high'] = df[['highAsk', 'highBid']].mean(axis=1)
    df['low'] = df[['lowAsk', 'lowBid']].mean(axis=1)
    df['close'] = df[['closeAsk', 'closeBid']].mean(axis=1)
    return df[['time', 'open', 'high', 'low', 'close']]


# Adds simple moving average to average bar dataframe
def add_sma(df, val):
    df['SMA {}'.format(val)] = df['close'].rolling(window=val).mean()


def add_2_sma(df, val, val2):
    if val > val2:
        temp = val
        val = val2
        val2 = temp
    df['SMA {}'.format(val)] = df['close'].rolling(window=val).mean()
    df['SMA {}'.format(val2)] = df['close'].rolling(window=val2).mean()


def add_state(df, sma):
    state = 'NA'
    col = 'SMA {}'.format(sma)
    for i in range(2, len(df)):
        if df[col].iloc[i] < df[col].iloc[i-1]:
            state = 'Below'
        elif df[col].iloc[i] > df[col].iloc[i-1]:
            state = 'Above'
        else:
            state = 'NA'
            
        df.ix[i, 'State {}'.format(sma)] = state


#Returns state of shorter moving average compared to the longer moving average
def compare_state(df, firstsma, secondsma):
    state = 'NA'
    for i in df.index:
        try:
            if Decimal(df.ix[i, firstsma]) < Decimal(df.ix[i, secondsma]):
                state = 'Below'
            elif Decimal(df.ix[i, firstsma]) > Decimal(df.ix[i, secondsma]):
                state = 'Above'
            else:
                state = 'NA'

            df.ix[i, 'State'] = state
        except:
            pass

def penultimate_bars_status(df, bars, sma):
    lst = []
    for i in range(2, bars+2):
        lst.append(df['State {}'.format(sma)].iloc[-i])
    return lst

def penultimate_bars_identical(df, bars, sma):
    pen_bars_status = penultimate_bars_status(df, bars, sma)
    return check_equal(pen_bars_status)

def last_bar_status(df, sma):
    return df['State {}'.format(sma)].iloc[-1]

def check_equal(lst):
    return lst[1:] == lst[:-1]

def pip_difference(price1, price2):
    return abs((Decimal(price1) - Decimal(price2)) * 10000)


def get_current_rate(instrument):
        url = 'https://api-fxpractice.oanda.com/v1/prices'
        headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
        params = {'accountId' : account_id,'instruments': instrument}
        req = requests.get(url, headers = headers, params = params)
        json_data = req.json()
        item = json_data['prices'][0]
        item['time'] = datetime.strftime(datetime.fromtimestamp(float(item['time'][:10])),'%Y-%m-%d %H:%M:%S')
        return item


def get_spread(instrument):
        url = 'https://api-fxpractice.oanda.com/v1/prices'
        headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
        params = {'accountId' : account_id,'instruments': instrument}
        req = requests.get(url, headers = headers, params = params)
        json_data = req.json()
        item = json_data['prices'][0]
        ask = item['ask']
        bid = item['bid']
        return round((ask - bid) * 10000, 2)

def get_balance():
        url = config.url + '/v3/accounts/{}'.format(config.account_id)
        headers = {'Authorization' : 'Bearer ' + config.access_token}
        req = requests.get(url, headers = headers)
        json = req.json()
        return Decimal(json['account']['balance'])

def get_open_positions():
        url = config.url + '/v3/accounts/{}'.format(config.account_id)
        headers = {'Authorization' : 'Bearer ' + config.access_token}
        req = requests.get(url, headers = headers)
        json = req.json()
        return int(json['account']['openPositionCount'])

def last_fill(ticker):
    sql = ("SELECT time, units FROM Log Where type = 'ORDER_FILL' ORDER BY time DESC LIMIT 1")
    cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                             host=sql_host, database='{}'.format(ticker))
    cursor = cnx.cursor()
    cursor.execute(sql)
    results = cursor.fetchone()
    cursor.close()
    cnx.close()
    return results;

