import config
import event
import handler
import strategy
import portfolio
import risk
import execution
import analysis as an
from datetime import datetime
import time


#SQL & API credentials. Store in config file.

access_token = config.access_token
account_id = config.account_id

sql_host = config.sql_host
sql_user = config.sql_user_analysis
sql_password = config.sql_password_analysis

dh = handler.DataHandler()
queue = event.EventQueue()
strategy = strategy.Strategy()
risk = risk.Risk('USDJPY', .5, 2)
portfolio = portfolio.Portfolio()
execution = execution.Execution('USD_JPY')

while True:

    queue.add_to_queue(dh.get_latest_rate())

    while len(queue.queue) != 0:
        next_event = queue.next_event()

        if next_event.type == 'tick':
            #Call strategy
            queue.add_to_queue(strategy.generate_signal(next_event))
            print(str(datetime.now()) + ':  ' + 'Strategy called')

        elif next_event.type == 'signal':
            # If signal requires, call risk
            if next_event.signal != 'none':
                queue.add_to_queue(risk.calculate_risk(next_event))
                print(str(datetime.now()) + ':  ' + 'Risk called')

        elif next_event.type == 'trade':
            #Call portfolio
            queue.add_to_queue(portfolio.check_order(next_event))
            print(str(datetime.now()) + ':  ' + 'Portfolio called')

        elif next_event.type == 'order':
            #Call execution
            execution.order(next_event)
            print(str(datetime.now()) + ':  ' + 'Execution called')

        elif next_event.type == 'close':
            execution.close_last_trade()
            print(str(datetime.now()) + ':  ' + 'Execution (close trade) called')
        
        elif next_event.type == 'none':
            print(str(datetime.now()) + ':  ' + 'Not passed')

        else:
            print(str(datetime.now()) + ':  ' + 'Queue Error')

    time.sleep(30)