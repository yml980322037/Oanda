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

ticker = 'GBP_USD'
queue = event.EventQueue()
strategy = strategy.MA_Strategy(ticker)
risk = risk.MA_Risk(ticker, 1, 2)
portfolio = portfolio.MATestPortfolio(300, 1)

dh = handler.HistoricalDataHandler(ticker, 'M1', datetime(2017, 2, 15, 0, 0, 0), datetime(2017, 2, 19, 0, 0, 0))
length = len(dh.df) - 1


for i in range(length):

    queue.add_to_queue(dh.push_next_ma_bar_1h())


    while len(queue.queue) != 0:
        event = queue.next_event()
        print('time: ', event.time, 'Balance: ', portfolio.balance, ' Open: ', portfolio.open_trade)

        if event.type == 'none':
            continue

        elif event.type == 'tick' and portfolio.open_trade and not (hasattr(event, 'plchecked')):
            queue.add_to_queue(portfolio.check_position(event))
            try:
                if portfolio.trade_details['signal'] == 'sell':
                    print('Position:  ', portfolio.trade_details['signal'])
                    print('From Entry:', (portfolio.trade_details['price']['bid'] - event.price['ask']) * 10000)
                    print('Price:     ', event.price['ask'])
                    print('SL:        ', portfolio.trade_details['sl'])
                    print('To SL:     ', an.pip_difference(portfolio.trade_details['sl'], event.price['ask']))
                    print('To TP:     ', an.pip_difference(portfolio.trade_details['tp'], event.price['ask']))
                elif portfolio.trade_details['signal'] == 'buy':
                    print('Position: ', portfolio.trade_details['signal'])
                    print('From Entry', (event.price['bid'] - portfolio.trade_details['price']['ask']) * 10000)
                    print('Price:    ', event.price['bid'])
                    print('SL:       ', portfolio.trade_details['sl'])
                    print('To SL:    ', an.pip_difference(portfolio.trade_details['sl'], event.price['bid']))
                    print('To TP:    ', an.pip_difference(portfolio.trade_details['tp'], event.price['bid']))
            except:
                pass
            
        elif event.type == 'tick' and portfolio.open_trade and not (hasattr(event, 'slchecked')):
            queue.add_to_queue(risk.check_sl(event, portfolio.trade_details))
            try:
                if portfolio.trade_details['signal'] == 'sell':
                    print('Position: ', portfolio.trade_details['signal'])
                    print('From Entry:', (portfolio.trade_details['price']['bid'] - event.price['ask']) * 10000)
                    print('Price:     ', event.price['ask'])
                    print('SL:        ', portfolio.trade_details['sl'])
                    print('To SL:     ', an.pip_difference(portfolio.trade_details['sl'], event.price['ask']))
                    print('To TP:     ', an.pip_difference(portfolio.trade_details['tp'], event.price['ask']))
                elif portfolio.trade_details['signal'] == 'buy':
                    print('Position: ', portfolio.trade_details['signal'])
                    print('From Entry', (event.price['bid'] - portfolio.trade_details['price']['ask']) * 10000)
                    print('Price:    ', event.price['bid'])
                    print('SL:       ', portfolio.trade_details['sl'])
                    print('To SL:    ', an.pip_difference(portfolio.trade_details['sl'], event.price['bid']))
                    print('To TP:    ', an.pip_difference(portfolio.trade_details['tp'], event.price['bid']))
            except:
                pass
        
        elif event.type == 'alter_trade':
            portfolio.alter_trade(event)

        elif event.type == 'tick':
            # Call strategy
            queue.add_to_queue(strategy.generate_signal(event, portfolio.open_trade))
            print(event.type)

        elif event.type == 'signal':
            queue.add_to_queue(risk.check_new_trade(event, portfolio.balance))

        elif event.type == 'trade':
            # Call portfolio
            portfolio.check_order(event)

        else:
            print('Queue Error')
    sys.stdout.flush()