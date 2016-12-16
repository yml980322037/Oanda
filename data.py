import requests
import json
from pandas import Series, DataFrame
from datetime import datetime
import config


# Store oanda api details in config file

url = config.url
access_token = config.access_token
account_id = config.account_id

# Create class to retrieve data and store in SQL Database


class Data:
    
    def __init__(self,ticker):
        self.ticker = ticker
        self.url = url
        self.headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
        self.params = {'accountId' : account_id,'instrument': self.ticker}
    
    def pull_json_data(self,startdate,enddate,starthr,endhr,granularity):
        self.params['start'] = datetime.timestamp(datetime.strptime(startdate+starthr,'%Y-%m-%d%H'))
        self.params['end'] = datetime.timestamp(datetime.strptime(enddate+endhr,'%Y-%m-%d%H'))
        self.params['granularity'] = granularity
        req = requests.get(self.url, headers = self.headers, params = self.params)
        json_data = req.json()
        self.params.pop('start', None)
        self.params.pop('end', None)
        return json_data['candles']
    
    
    #Change function to loop through stored 3hr dataframe instead of API call
    def check_3hr_trend(self,time):
        self.params['count'] = 15
        self.params['end'] = datetime.timestamp(datetime.strptime(time,'%Y-%m-%d%H:%M:%S'))
        self.params['granularity'] = 'H3'
        
        req = requests.get(self.url, headers = self.headers, params = self.params)
        json_data = req.json()
        json_data = json_data['candles']
        time_reformatter(json_data)
        
        df = DataFrame(json_data)
        add_sma3_sma10(df)
        
        if df.ix[11, 'SMA10'] < df.ix[14, 'SMA10']:
            return True
        
    

# Reformats time from UNIX Timestamp to date and time in string format   
def time_reformatter(datadict):
    for item in datadict:
        item['date'] = datetime.strftime(datetime.fromtimestamp(float(item['time'][:10])),'%Y-%m-%d')
        item['time'] = datetime.strftime(datetime.fromtimestamp(float(item['time'][:10])),'%H:%M:%S')
        item.pop('volume', None)
        item.pop('complete', None)


# Add SMA 3 and 10 as dataframe columns - Change function so that it takes period as a parameter
def add_sma3_sma10(df):
    df['SMA3'] = df['openBid'].rolling(window=3).mean()
    df['SMA10'] = df['openBid'].rolling(window=10).mean()


def add_state(df):
    state = 'Above'
    for i in df.index:
        if df.ix[i, 'SMA3'] < df.ix[i, 'SMA10']:
            state = 'Below'
        else:
            state = 'Above'

        df.ix[i, 'State'] = state



#Create function to check trend from SMA10? - Return Boolean - Work on DataFrame index
def check_trend(df, index):
    if df.ix[index-20, 'SMA10'] < df.ix[index, 'SMA10']:
        return True



def crosses(df):
	crosses = 0

	for i in df.index[20:]:
	    if check_trend(df, i):
	        if df.ix[i-1,'State'] == 'Below' and df.ix[i, 'State'] == 'Above' : # True when SMA3 crosses over SMA10
	            diff = ((df.ix[i, 'SMA10'] - df.ix[i-15, 'SMA10']) / df.ix[i, 'SMA10']) * 100
	            spread = (df.ix[i, 'openAsk'] - df.ix[i, 'openBid']) *100
	            print('{} at {} {}, Spread: {}'.format(
	                    round(diff, 6), df.ix[i, 'time'],df.ix[i, 'date'], round(spread ,9)))
	            crosses += 1

print('Crossed above {} times.'.format(crosses))



def crosses_with_3hr(dataframe):
    cross = 0
    for i in dataframe.index[20:]:
            if check_trend(dataframe, i):
                if USD_JPY.check_3hr_trend(dataframe.ix[i, 'date'] + dataframe.ix[i, 'time']):
                    if dataframe.ix[i-1,'State'] == 'Below' and dataframe.ix[i, 'State'] == 'Above' : # True when SMA3 crosses over SMA10
                        spread = (dataframe.ix[i, 'openAsk'] - dataframe.ix[i, 'openBid']) *100
                        print('{} {}, Spread: {}'.format(
                                dataframe.ix[i, 'time'],dataframe.ix[i, 'date'], round(spread ,9)))
                        cross += 1

    print('Crossed above {} times.'.format(cross))



