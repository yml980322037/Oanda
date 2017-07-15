import config
import requests
import json
from datetime import datetime
from datetime import timedelta
import mysql.connector

class Execution:

	def __init__(self, ticker):
		self.ticker = ticker
		self.last_trade_ID = '-1'


	def order(self, event_object):
		units = event_object.units
		sl = event_object.sl
		tp = event_object.tp
		url = 'https://api-fxpractice.oanda.com/v3/accounts/{}/orders'.format(config.account_id)
		headers = {'Authorization' : 'Bearer ' + config.access_token, 'Content-Type': 'application/json', 'Accept-Datetime-Format': 'UNIX'}
		stop_loss = {'price': str(sl)}
		take_profit = {'price': str(tp)}
		data = {'order':{'units': str(units), 'instrument': self.ticker, 'timeInForce': 'FOK',
		'type': 'MARKET', 'stopLossOnFill': stop_loss, 'takeProfitOnFill': take_profit, 'positionFill': 'DEFAULT'}}
		req = requests.post(url, headers = headers, data = json.dumps(data))
		json_data = req.json()
		print('TP: ', take_profit)
		print('SL: ', stop_loss)
		print('Units: ', units)
		print (json_data)
		self.last_trade_ID = json_data['orderFillTransaction']['id']
		self.log_to_db(json_data)


	def close_last_trade(self):
		url = 'https://api-fxpractice.oanda.com/v3/accounts/{}/trades/{}/close'.format(config.account_id, self.last_trade_ID)
		headers = {'Authorization' : 'Bearer ' + config.access_token, 'Content-Type': 'application/json', 'Accept-Datetime-Format': 'UNIX'}
		req = requests.put(url, headers = headers)
		json_data = req.json()
		self.last_trade_ID = '-1'
		return json_data


	def log_to_db(self, order_response):
		# If statements to call correct method
		for key, value in order_response.items():
			if key == 'orderCreateTransaction':
				self.log_order_create_transaction(value)
			elif key == 'orderFillTransaction':
				self.log_order_fill_transaction(value)
			elif key == 'orderCancelTransaction':
				self.log_order_cancel_transaction(value)
		


	def log_order_create_transaction(self,json_data):
		self.time_reformatter(json_data)
		json_data['stopLossOnFill'] = json_data['stopLossOnFill']['price']
		json_data['takeProfitOnFill'] = json_data['takeProfitOnFill']['price']
		add_row = ("INSERT INTO Log"
			"(id, batch_id, time, type, reason, units, stop_loss, take_profit) "
			"VALUES (%(id)s, %(batchID)s, %(time)s, %(type)s, %(reason)s, "
			"%(units)s, %(stopLossOnFill)s, %(takeProfitOnFill)s)")
		self.execute_db_query(add_row, json_data)

	def log_order_fill_transaction(self,json_data):
		data = json_data
		self.time_reformatter(data)
		data['tradeOpened'] = '0'
		add_row = ("INSERT INTO Log"
			"(id, batch_id, time, type, reason, price, units, financing, account_balance) "
			"VALUES (%(id)s, %(batchID)s, %(time)s, %(type)s, %(reason)s, "
			"%(price)s, %(units)s, %(financing)s, %(accountBalance)s)")
		self.execute_db_query(add_row, data)


	def log_order_cancel_transaction(self, json_data):
		data = json_data
		self.time_reformatter(data)
		add_row = ("INSERT INTO Log"
			"(id, batch_id, time, type, reason) "
			"VALUES (%(id)s, %(batchID)s, %(time)s, %(type)s, %(reason)s)")
		self.execute_db_query(add_row, data)


	def execute_db_query(self, query, data):
		cnx = mysql.connector.connect(user=config.sql_user_sourcefeed, password=config.sql_password_sourcefeed,
			host=config.sql_host, database='{}'.format(self.ticker))
		cursor = cnx.cursor()
		cursor.execute(query, data)
		cnx.commit()
		cursor.close()
		cnx.close()


	def create_log_table(self):
		create = ("CREATE TABLE IF NOT EXISTS Log"
			"(id INTEGER UNIQUE, batch_id INTEGER, time DATETIME, type CHAR(15), reason CHAR(15), price DECIMAL(6,3), "
			" units INTEGER, pl DECIMAL(8,3), financing DECIMAL(8,3), stop_loss DECIMAL(6,3), take_profit DECIMAL(6,3), "
			"account_balance DECIMAL(15,5))")
		cnx = mysql.connector.connect(user=config.sql_user_sourcefeed, password=config.sql_password_sourcefeed,
			host=config.sql_host, database='{}'.format(self.ticker))
		cursor = cnx.cursor()
		cursor.execute(create)
		cursor.close()
		cnx.close()


	def time_reformatter(self, json_data):
		json_data['time'] = datetime.strftime((datetime.fromtimestamp(float(json_data['time'][:10])) + timedelta(hours = 1)),'%Y-%m-%d %H:%M:%S') 









