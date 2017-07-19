# Change to Abstract class
import config
import requests
from decimal import Decimal
import analysis as an

class Portfolio:
    
    def __init__(self):
        #initialist balance, margin requirement, pull existing open trades.
        self.update()
        self.start_balance = self.balance
        self.percentage_change()


    def check_order(self, event_object):
        ev = event_object
        self.update()
        self.percentage_change()
        if self.pct_change > -3 or ev.spread < 2 or ev.margin_total < (self.balance * 0.6):
            ev.type = 'order'
            return ev
        else:
            ev.type = 'none'
            return ev        
        
    
    def update(self):
        summary = self.account_summary()
        self.balance = float(summary['balance'])
        self.currency = summary['currency']
        self.margin_available = summary['marginAvailable']
        self.margin_used = summary['marginUsed']
        self.positions = summary['openPositionCount']


    def account_summary(self):
        self.url = config.url + '/v3/accounts/{}'.format(config.account_id)
        self.headers = {'Authorization' : 'Bearer ' + config.access_token}
        req = requests.get(self.url, headers = self.headers)
        json = req.json()
        return json['account']

    
    def percentage_change(self):
        self.pct_change = round((self.balance - self.start_balance) / self.start_balance * 100, 2)



class MTLTestPortfolio:
    
    def __init__(self, balance, riskpct):
        #initialist balance, margin requirement, pull existing open trades.
        self.start_balance = Decimal(balance)
        self.balance = Decimal(balance)
        self.riskpct = Decimal(riskpct/100)
        self.pct_change = 0
        self.open_trade = False
        self.trade_details = None
        self.log_loss = []
        self.log_profit = []


    def check_order(self, event_object):
        ev = event_object
        if self.pct_change > -3 or ev.margin_total < (self.balance * 0.6):
            ev.type = 'order'
            self.log_trade(ev)
            

    def log_trade(self, ev):
        self.open_trade = True
        self.trade_details = {'time': ev.time, 'sl': ev.sl, 'tp': ev.tp, 'open_sl': ev.sl, 'open_tp': ev.tp , 'signal': ev.signal, 'price': ev.price,
        'event': ev, 'spread': ev.spread, 'pip_value': ev.pip_value, 'reward': ev.reward}


    def check_position(self, event):
        ev = event
        if self.trade_details['signal'] == 'buy':
            if ev.price['bid'] <= self.trade_details['sl']:
                if self.trade_details['sl'] == self.trade_details['price']['ask']:
                    print('Break Even')
                    return self.close_at_break_even(event)
                elif self.trade_details['sl'] > self.trade_details['price']['ask']:
                    print('TS Triggered')
                    self.balance += (self.balance * self.riskpct) * (self.trade_details['sl'] / self.trade_details['open_sl'])
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev
                else:
                    print('SL Triggered')
                    self.balance -= self.balance * self.riskpct
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev

            elif ev.price['bid'] >= self.trade_details['tp']:
                print('TP Triggered')
                self.balance += self.balance * self.riskpct * self.trade_details['reward']
                self.log_profit.append(self.trade_details)
                self.open_trade = False
                self.trade_details = None
                ev.type = 'none'
                return ev
            else:
                ev.plchecked = True
                return ev
        elif self.trade_details['signal'] == 'sell':
            if ev.price['ask'] >= self.trade_details['sl']:
                if self.trade_details['sl'] == self.trade_details['price']['bid']:
                    print('Break Even')
                    return self.close_at_break_even(event)
                elif self.trade_details['sl'] < self.trade_details['price']['bid']:
                    print('TS Triggered')
                    self.balance += self.balance * self.riskpct * (self.trade_details['sl'] / self.trade_details['open_sl'])
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev
                else:
                    print('SL Triggered')
                    self.balance -= self.balance * self.riskpct
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev

            elif ev.price['ask'] <= self.trade_details['tp']:
                print('TP Triggered')
                self.balance += self.balance * self.riskpct * self.trade_details['reward']
                self.trade_details['closed'] = event.price['ask']
                self.log_profit.append(self.trade_details)
                self.open_trade = False
                self.trade_details = None
                ev.type = 'none'
                return ev

            else:
                ev.plchecked = True
                return ev
        else:
            ev.plchecked = True
            return ev


    def alter_trade(self, event):
        self.trade_details = event.trade_details

    def close_at_break_even(self, event):
        self.trade_details['closed'] = self.trade_details['sl']
        self.log_loss.append(self.trade_details)
        self.open_trade = False
        self.trade_details = None
        event.type = 'none'
        return event
    
    def percentage_change(self):
        self.pct_change = round((self.balance - self.start_balance) / self.start_balance * 100, 2)






class MATestPortfolio:
    
    def __init__(self, balance, riskpct):
        #initialist balance, margin requirement, pull existing open trades.
        self.start_balance = Decimal(balance)
        self.balance = Decimal(balance)
        self.riskpct = Decimal(riskpct/100)
        self.pct_change = 0
        self.open_trade = False
        self.trade_details = None
        self.log_loss = []
        self.log_profit = []


    def check_order(self, event_object):
        ev = event_object
        if self.pct_change > -3 or ev.margin_total < (self.balance * 0.6):
            ev.type = 'order'
            self.log_trade(ev)
            

    def log_trade(self, ev):
        self.open_trade = True
        self.trade_details = {'time': ev.time, 'sl': ev.sl, 'tp': ev.tp, 'open_sl': ev.sl, 'open_tp': ev.tp , 'signal': ev.signal, 'price': ev.price,
        'event': ev, 'spread': ev.spread, 'pip_value': ev.pip_value, 'open_pip_sl': ev.pip_stop_loss, 'reward': ev.reward}


    def check_position(self, event):
        ev = event
        if self.trade_details['signal'] == 'buy':
            if ev.price['bid'] <= self.trade_details['sl']:
                if self.trade_details['sl'] == self.trade_details['price']['ask']:
                    print('Break Even')
                    return self.close_at_break_even(event)

                elif self.trade_details['sl'] > self.trade_details['price']['ask']:
                    print('TS Triggered')
                    self.balance += (self.balance * self.riskpct) * (self.trade_details['pip_sl'] / self.trade_details['open_pip_sl'])
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev

                else:
                    print('SL Triggered')
                    self.balance -= self.balance * self.riskpct
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev

            elif ev.price['bid'] >= self.trade_details['tp']:
                print('TP Triggered')
                self.balance += self.balance * self.riskpct * self.trade_details['reward']
                self.log_profit.append(self.trade_details)
                self.open_trade = False
                self.trade_details = None
                ev.type = 'none'
                return ev
            else:
                ev.plchecked = True
                return ev
        elif self.trade_details['signal'] == 'sell':
            if ev.price['ask'] >= self.trade_details['sl']:
                if self.trade_details['sl'] == self.trade_details['price']['bid']:
                    print('Break Even')
                    return self.close_at_break_even(event)

                elif self.trade_details['sl'] < self.trade_details['price']['bid']:
                    print('TS Triggered')
                    self.balance += self.balance * self.riskpct * (self.trade_details['pip_sl'] / self.trade_details['open_pip_sl'])
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev
                
                else:
                    print('SL Triggered')
                    self.balance -= self.balance * self.riskpct
                    self.log_loss.append(self.trade_details)
                    self.open_trade = False
                    self.trade_details = None
                    ev.type = 'none'
                    return ev

            elif ev.price['ask'] <= self.trade_details['tp']:
                print('TP Triggered')
                self.balance += self.balance * self.riskpct * self.trade_details['reward']
                self.trade_details['closed'] = event.price['ask']
                self.log_profit.append(self.trade_details)
                self.open_trade = False
                self.trade_details = None
                ev.type = 'none'
                return ev

            else:
                ev.plchecked = True
                return ev
        else:
            ev.plchecked = True
            return ev


    def alter_trade(self, event):
        self.trade_details = event.trade_details

    def close_at_break_even(self, event):
        self.trade_details['closed'] = self.trade_details['sl']
        self.log_loss.append(self.trade_details)
        self.open_trade = False
        self.trade_details = None
        event.type = 'none'
        return event
    
    def percentage_change(self):
        self.pct_change = round((self.balance - self.start_balance) / self.start_balance * 100, 2)