import config
import event
import handler
import strategy
import portfolio
import risk
import execution
import analysis as an
from datetime import datetime
from datetime import timedelta
import time
import sys


#SQL & API credentials. Store in config file.

access_token = config.access_token
account_id = config.account_id

sql_host = config.sql_host
sql_user = config.sql_user_analysis
sql_password = config.sql_password_analysis

dh = handler.DataHandler()
queue = event.EventQueue()
strategy = strategy.Strategy('GBP_USD')
risk = risk.Risk('GBP_USD', .9, 2)
portfolio = portfolio.Portfolio()
execution = execution.Execution('GBP_USD')
execution.create_log_table()

while True:

    try:

        queue.add_to_queue(dh.get_latest_rate('GBP_USD'))


        while len(queue.queue) != 0:
            timenow = datetime.utcnow() + timedelta(hours = 1)
            next_event = queue.next_event()

            if next_event.type == 'tick':
                #Call strategy
                queue.add_to_queue(strategy.generate_signal(next_event))
                print(str(timenow) + ':  ' + 'Strategy called')

            elif next_event.type == 'signal':
                # If signal requires, call risk
                if next_event.signal != 'none':
                    queue.add_to_queue(risk.calculate_risk(next_event))
                    print(str(timenow) + ':  ' + 'Risk called')

            elif next_event.type == 'trade':
                #Call portfolio
                queue.add_to_queue(portfolio.check_order(next_event))
                print(str(timenow) + ':  ' + 'Portfolio called')

            elif next_event.type == 'order':
                #Call execution
                execution.order(next_event)
                print(str(timenow) + ':  ' + 'Execution called')

            elif next_event.type == 'close':
                execution.close_last_trade()
                print(str(timenow) + ':  ' + 'Execution (close trade) called')
            
            elif next_event.type == 'none':
                print(str(timenow) + ':  ' + 'Not passed')

            else:
                print(str(timenow) + ':  ' + 'Queue Error')

    except Exception as e:
        print('Loop failed')
        print(repr(e))


    print('')

    sys.stdout.flush()
    time.sleep(30)