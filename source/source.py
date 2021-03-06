
# This module is used to gather data pulled using the Oanda REST API into an SQL database


import requests
import json
from datetime import datetime, timedelta
import config
import mysql.connector
from mysql.connector import errorcode


# Store oanda api & SQL Server authentication in config file

url = config.url
access_token = config.access_token
account_id = config.account_id

sql_host = config.sql_host
sql_user = config.sql_user_sourcefeed
sql_password = config.sql_password_sourcefeed



class Source:
    
    # Currency pair has to be separated by underscore
    def __init__(self,ticker):
        self.ticker = ticker
        self.url = url + '/v1/candles'
        self.headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
        self.params = {'accountId' : account_id,'instrument': self.ticker}
    
    def pull_json_data(self, starttime, endtime, granularity):
        self.params['start'] = datetime.timestamp(datetime.strptime(starttime,'%Y-%m-%d %H:%M:%S'))
        self.params['end'] = datetime.timestamp(datetime.strptime(endtime,'%Y-%m-%d %H:%M:%S'))
        self.params['granularity'] = granularity
        req = requests.get(self.url, headers = self.headers, params = self.params)
        self.params.pop('start', None)
        self.params.pop('end', None)
        json_data = req.json()
        return json_data['candles']

    def pull_json_data_by_len(self, starttime, count, granularity):
        self.params['start'] = datetime.timestamp(datetime.strptime(starttime,'%Y-%m-%d %H:%M:%S'))
        self.params['count'] = count
        self.params['granularity'] = granularity
        req = requests.get(self.url, headers = self.headers, params = self.params)
        self.params.pop('start', None)
        self.params.pop('count', None)
        json_data = req.json()
        return json_data['candles']
    
    # Retrieve & store returned data into correct table using parameter - Use add to table
    def pull_to_table(self, starttime, endtime, granularity):
        json_data = self.pull_json_data(starttime, endtime, granularity)
        time_reformatter(json_data)
        self.add_to_table(json_data, granularity)

    def pull_to_table_by_len(self, starttime, count, granularity):
        json_data = self.pull_json_data_by_len(starttime, count, granularity)
        time_reformatter(json_data)
        self.add_to_table(json_data, granularity)
    
    
    def add_to_table(self,json_dict,granularity):
        add_row = ("INSERT IGNORE INTO {}"
                   "(time, openask, closeask, lowask, highask, openbid, closebid, lowbid, highbid, volume)"
                   "VALUES (%(time)s, %(openAsk)s, %(closeAsk)s, %(lowAsk)s, %(highAsk)s, "
                   "%(openBid)s, %(closeBid)s, %(lowBid)s, %(highBid)s, %(volume)s)"
                   "ON DUPLICATE KEY UPDATE "
                   "closeask = %(closeAsk)s,"
                   "lowask = %(lowAsk)s,"
                   "highask = %(highAsk)s,"
                   "closebid = %(closeBid)s,"
                   "lowbid = %(lowBid)s,"
                   "highbid = %(highBid)s,"
                   "volume = %(volume)s".format(granularity))
        
        cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                                 host=sql_host, database='{}'.format(self.ticker))
        cursor = cnx.cursor()
        for i in json_dict:
            cursor.execute(add_row, i)
        cnx.commit()
        cursor.close()
        cnx.close()
        
    def create_table(self, granularity):
        create = ("CREATE TABLE IF NOT EXISTS {}"
                  "(time datetime unique, openask decimal(6,5), closeask decimal(6,5), lowask decimal(6,5), "
                  "highask decimal(6,5), openbid decimal(6,5), closebid decimal(6,5), lowbid decimal(6,5), "
                  "highbid decimal(6,5), volume int(10))".format(granularity))
        cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                                 host=sql_host, database='{}'.format(self.ticker))
        cursor = cnx.cursor()
        cursor.execute(create)
        cursor.close()
        cnx.close()
        
    def halted(self):
        url = 'https://api-fxpractice.oanda.com/v1/prices'
        headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
        params = {'accountId' : account_id,'instruments': self.ticker}
        req = requests.get(url, headers = headers, params = params)
        json_data = req.json()
        item = json_data['prices'][0]
        if 'status' in item:
            return True
        else:
            return False

    def get_instrument_list(self):
      url = 'https://api-fxpractice.oanda.com/v3/accounts/{}/instruments'.format(config.account_id)
      headers = {'Authorization' : 'Bearer ' + access_token,'X-Accept-Datetime-Format': 'UNIX'}
      req = requests.get(url, headers = headers)
      json_data = req.json()
      return json_data




    ### TEST
    '''
    from dateutil import rrule
    import datetime

    for i in rrule.rrule(rrule.HOURLY, interval = 5, dtstart=datetime.datetime(2017,7,6), until=datetime.datetime(2017,7,8)):
    time = datetime.datetime.strftime(i, '%Y-%m-%d %H:%M:%S')
    print(time)
    GBP_USD.pull_to_table_by_len(time, 5000, 'S5')'''




# Takes dictionary as parameter - Changes UNIX Timestamp to Datetime format for SQL Table
# Change for DST
def time_reformatter(json_data):
    for item in json_data:
        item['time'] = datetime.strftime(datetime.utcfromtimestamp(float(item['time'][:10])) + timedelta(hours = 1),'%Y-%m-%d %H:%M:%S')



