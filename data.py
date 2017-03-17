import requests
import json
from datetime import datetime
import config
import mysql.connector
from mysql.connector import errorcode


# Store oanda api & SQL Server authentication in config file
url = config.url
access_token = config.access_token
account_id = config.account_id

sql_host = config.sql_host
sql_user = config.sql_user
sql_password = config.sql_password


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
        self.params.pop('start', None)
        self.params.pop('end', None)
        json_data = req.json()
        return json_data['candles']
    
    def get_current_rate(self):
        url = 'https://api-fxpractice.oanda.com/v1/prices'
        self.params['instruments'] = self.ticker
        req = requests.get(url, headers = self.headers, params = self.params)
        json_data = req.json()
        self.params.pop('instruments', None)
        time_reformatter(json_data['prices'])
        return json_data['prices'][0]
        
    
    # Retrieve & store returned data into correct table using parameter - Use add to table
    def pull_to_table(self, startdate, enddate, starthr, endhr, granularity):
        json_data = self.pull_json_data(startdate, enddate, starthr, endhr, granularity)
        time_reformatter(json_data)
        self.create_table(granularity)
        self.add_to_table(json_data, granularity)
    
    
    def add_to_table(self,json_dict,granularity):
        add_row = ("INSERT IGNORE INTO {}"
                   "(time, openask, closeask, lowask, highask, openbid, closebid, lowbid, highbid, volume)"
                   "VALUES (%(time)s, %(openAsk)s, %(closeAsk)s, %(lowAsk)s, %(highAsk)s, "
                   "%(openBid)s, %(closeBid)s, %(lowBid)s, %(highBid)s, %(volume)s)".format(granularity))
        
        cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                                 host=sql_host, database='USDJPY')
        cursor = cnx.cursor()
        for i in json_dict:
            cursor.execute(add_row, i)
        cnx.commit()
        cursor.close()
        cnx.close()
        
    def create_table(self, granularity):
        create = ("CREATE TABLE IF NOT EXISTS {}"
                  "(time datetime unique, openask decimal(6,3), closeask decimal(6,3), lowask decimal(6,3), "
                  "highask decimal(6,3), openbid decimal(6,3), closebid decimal(6,3), lowbid decimal(6,3), "
                  "highbid decimal(6,3), volume int(10))".format(granularity))
        cnx = mysql.connector.connect(user=sql_user, password=sql_password,
                                 host=sql_host, database='USDJPY')
        cursor = cnx.cursor()
        cursor.execute(create)
        cursor.close()
        cnx.close()
        
        
# Takes dictionary as parameter - Changes UNIX Timestamp to Datetime format for SQL Table
def time_reformatter(datadict):
    for item in datadict:
        item['time'] = datetime.strftime(datetime.fromtimestamp(float(item['time'][:10])),'%Y-%m-%d %H:%M:%S')