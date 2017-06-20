import source
from datetime import datetime, timedelta
import time

USD_JPY = source.Source('USD_JPY')

# Creates table if not on DB
USD_JPY.create_table('M15')
USD_JPY.create_table('H3')

USD_JPY.pull_to_table(datetime.strftime(timenow - timedelta(hours = 6),'%Y-%m-%d %H:%M:%S'),
	                              datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'M15')
USD_JPY.pull_to_table(datetime.strftime(timenow - timedelta(days = 3),'%Y-%m-%d %H:%M:%S'),
	                              datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'H3')


while True:
	# Change for Daylight Saving Time
	timenow = datetime.utcnow() + timedelta(hours = 1)

	if USD_JPY.halted() == False:
	    try:
	        USD_JPY.pull_to_table(datetime.strftime(timenow - timedelta(minutes = 50),'%Y-%m-%d %H:%M:%S'),
	                              datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'M15')
	    except ValueError:
	        print('JSON Value Error')

	    try:
	        USD_JPY.pull_to_table(datetime.strftime(timenow - timedelta(hours = 10),'%Y-%m-%d %H:%M:%S'),
	                              datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'H3')
	    except ValueError:
	        print('JSON Value Error')


	time.sleep(5)