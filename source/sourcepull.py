import source
from datetime import datetime, timedelta
import time
import sys

GBP_USD = source.Source('GBP_USD')

# Creates table if not on DB
GBP_USD.create_table('S5')

timenow = datetime.utcnow() + timedelta(hours = 1)
GBP_USD.pull_to_table(datetime.strftime(timenow - timedelta(hours = 4),'%Y-%m-%d %H:%M:%S'),
	                              datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'S5')
print('Initialised')
time.sleep(3)


while True:

	try:
	# Change for Daylight Saving Time
		timenow = datetime.utcnow() + timedelta(hours = 1)

		GBP_USD.pull_to_table(datetime.strftime(timenow - timedelta(minutes = 5),'%Y-%m-%d %H:%M:%S'), 
			datetime.strftime(timenow + timedelta(minutes = 2),'%Y-%m-%d %H:%M:%S'), 'S5')

		sys.stdout.flush()

	except:
		print('Pull failed')

	time.sleep(3)