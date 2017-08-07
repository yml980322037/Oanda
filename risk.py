# Testing on GBP_USD
# Implement Abstract classes
import event
import analysis as an
from decimal import Decimal
from datetime import timedelta


class MA_Risk:
    
    def __init__(self, instrument, riskpct, marginpct):
        self.instrument = instrument
        self.riskpct = Decimal(riskpct/100)
        self.marginpct = Decimal(marginpct/100)
        self.spread_limit = Decimal(3)
        self.reward = Decimal(2)
        self.initial_stop_change = Decimal(0.0005)
        self.trailing_stop = Decimal(0.002)
        

    def check_new_trade(self, event, balance):
        ev = event
        ev.type = 'trade'
        ev.riskpct = self.riskpct
        ev.sl, ev.tp = self.sl_tp_calculator(ev, ev.signal)
        ev.pip_stop_loss = self.pip_stop_loss_calculator(ev.signal, ev.price, ev.sl)
        ev.pip_value = (balance * self.riskpct) / ev.pip_stop_loss
        ev.reward = self.reward
        ev.units = self.position_size_calculator(balance, self.riskpct, ev.signal, ev.price, ev.pip_stop_loss)
        ev.margin = self.margin_requirement(ev.units, self.marginpct)
        ev.margin_total = ev.margin + (balance * self.riskpct)

        if ev.signal == 'buy':
            price = ev.price['ask']
        elif ev.signal == 'sell':
            price = ev.price['bid']

        if ev.sl == 0 or ev.tp == 0:
            print('SL/TP not calculated')
            ev.type = 'none'
            return ev

        if ev.spread > self.spread_limit:
            print('Spread too high')
            ev.type = 'none'
            return ev

        if ev.pip_stop_loss - ev.spread < Decimal(7.5):
            print('SL too close')
            ev.type = 'none'
            return ev
        
        if abs(price - Decimal(ev.df['SMA 5'].iloc[-1])) * 10000 > Decimal(15):
            print('Too far from SMA')
            ev.type = 'none'
            return ev


        return ev



    def check_sl(self, event, trade_details):
        if trade_details['signal'] == 'buy':
            if event.price['bid'] - self.trailing_stop >= trade_details['sl'] and 'be' in trade_details.keys():
                event.type = 'alter_trade'
                event.trade_details = trade_details
                event.trade_details['sl'] = event.price['bid'] - self.trailing_stop
                event.trade_details['pip_sl'] = an.pip_difference(event.trade_details['sl'], event.trade_details['price']['ask'])
                event.slchecked = True
                return event
            elif event.price['bid'] - self.initial_stop_change >= trade_details['price']['ask'] and 'be' not in trade_details.keys():
                event.type = 'alter_trade'
                event.trade_details = trade_details
                event.trade_details['sl'] = event.trade_details['price']['ask']
                event.trade_details['be'] = True
                event.slchecked = True
                return event
            else:
                event.type = 'none'
                return event

        elif trade_details['signal'] == 'sell':
            if event.price['ask'] + self.trailing_stop <= trade_details['sl'] and 'be' in trade_details.keys():
                event.type = 'alter_trade'
                event.trade_details = trade_details
                event.trade_details['sl'] = event.price['ask'] + self.trailing_stop
                event.trade_details['pip_sl'] = an.pip_difference(event.trade_details['sl'], event.trade_details['price']['bid'])
                event.slchecked = True
                return event
            elif event.price['ask'] + self.initial_stop_change <= trade_details['price']['bid'] and 'be' not in trade_details.keys():
                event.type = 'alter_trade'
                event.trade_details = trade_details
                event.trade_details['sl'] = trade_details['price']['bid']
                event.trade_details['be'] = True
                event.slchecked = True
                return event
            else:
                event.type = 'none'
                return event
        else:
            event.type = 'none'
            return event


    def sl_tp_calculator(self, event, signal):
        if signal == 'buy':
            price = event.price['ask']
            sl = round(Decimal(min(event.df[-5:]['low'])), 5)
            diff = price - sl
            tp = round(price + diff * self.reward, 5)
            return sl, tp

        elif signal == 'sell':
            price = event.price['bid']
            sl = round(Decimal(max(event.df[-5:]['high'])), 5)
            diff = (sl - price)
            tp = round(price - diff * self.reward, 5)
            return sl, tp
        else:
            return 0, 0

            
    def position_size_calculator(self, balance, riskpct, signal, price, pipstoploss):
        if signal == 'buy':
            return round((((balance*riskpct)*price['ask']) / (pipstoploss/10000)))
        elif signal == 'sell':
            return -round((((balance*riskpct)*price['bid']) / (pipstoploss/10000)))

    def pip_stop_loss_calculator(self, signal, price, stoploss):
        if signal == 'buy':
            return round((price['ask'] - stoploss)*10000, 2)
        elif signal == 'sell':
            return round((stoploss - price['bid'])*10000, 2)

    def pip_take_profit_calculator(self, signal, price, takeprofit):
        if signal == 'buy':
            return an.pip_difference(price['ask'], takeprofit)
        elif signal == 'sell':
            return an.pip_difference(price['bid'], takeprofit)

        
    def margin_requirement(self, units, marginpct):
        margin = units * marginpct
        if margin < 0:
            return -margin
        return margin


    

class MR_Risk:
    
    def __init__(self, instrument, riskpct, marginpct):
        self.instrument = instrument
        self.riskpct = Decimal(riskpct/100)
        self.marginpct = Decimal(marginpct/100)

    def calculate_risk(self, event_object):
        balance = 300
        ev = event_object
        ev.type = 'trade'
        ev.riskpct = self.riskpct
        ev.lt_sma_est = self.lt_sma_estimate(ev.df)
        ev.pips_to_sma = self.pips_to_sma_calculator(ev)
        ev.min_pip_sl = ev.spread + Decimal(1.1)
        ev.sl, ev.tp = self.sl_tp_calculator(ev, event_object.signal)
        ev.pip_stop_loss = self.pip_stop_loss_calculator(ev.signal, ev.price, ev.sl)
        ev.pip_take_profit = self.pip_take_profit_calculator(ev.signal, ev.price, ev.tp)
        
        if ev.pips_to_sma > ev.pip_take_profit:
            if ev.signal == 'buy':
                ev.tp = ev.price['ask'] + (ev.pips_to_sma * Decimal(0.8) / 10000)
            elif ev.signal == 'sell':
                ev.tp = ev.price['bid'] - (ev.pips_to_sma * Decimal(0.8) / 10000)

            ev.pip_take_profit = self.pip_take_profit_calculator(ev.signal, ev.price, ev.tp)

        ev.reward = ev.pip_take_profit/ev.pip_stop_loss
        print(ev.signal)
        print('Reward: ', ev.reward)
        print('Pips to LT SMA: ', ev.pips_to_sma)
        print('SL: ', ev.pip_stop_loss)
        print('TP: ', ev.pip_take_profit)


        if ev.pips_to_sma < ev.pip_take_profit or ev.pips_to_sma < Decimal(8.2):
            ev.type = 'none'
            print('LT_SMA TOO CLOSE')

        ev.units = self.position_size_calculator(balance, self.riskpct, ev.signal, ev.price, ev.pip_stop_loss)
        ev.margin = self.margin_requirement(ev.units, self.marginpct)
        ev.margin_total = ev.margin + (balance * self.riskpct)

        return ev


    def lt_sma_estimate(self, df):
        arr = [round(Decimal(x), 5) for x in df['SMA 15'][-5:-1]]
        changes = []
        for i in range(1, len(arr)):
            changes.append((arr[i] - arr[i-1]))
        return round(Decimal(df['SMA 15'].iloc[-1]) + changes[0] + changes[1] + changes[2], 5)


    def pips_to_sma_calculator(self, ev):
        if ev.signal == 'buy':
            return an.pip_difference(ev.lt_sma_est, ev.price['ask'])
        elif ev.signal == 'sell':
            return an.pip_difference(ev.lt_sma_est, ev.price['bid'])
        else:
            return 0

        
    def sl_tp_calculator(self, event, signal):
        if signal == 'buy':
            price = event.price['ask']
            sl = round(Decimal(min(event.df['low'].iloc[-2:])), 5)
            if an.pip_difference(price, sl) < event.min_pip_sl:
                sl -= event.min_pip_sl / 10000
            diff = price - sl
            tp = round(price + (diff * Decimal(1.5)), 5)
            return (sl, tp)

        elif signal == 'sell':
            price = event.price['bid']
            sl = round(Decimal(max(event.df['high'].iloc[-2:])), 5)
            if an.pip_difference(price, sl) < event.min_pip_sl:
                sl += event.min_pip_sl / 10000
            diff = (sl - price)
            tp = round(price - (diff * Decimal(1.5)), 5)
            return (sl, tp)
        else:
            return (0,0)


    def pip_stop_loss_calculator(self, signal, price, stoploss):
        if signal == 'buy':
            return an.pip_difference(price['ask'], stoploss)
        elif signal == 'sell':
            return an.pip_difference(price['bid'], stoploss)


    def pip_take_profit_calculator(self, signal, price, takeprofit):
        if signal == 'buy':
            return an.pip_difference(price['ask'], takeprofit)
        elif signal == 'sell':
            return an.pip_difference(price['bid'], takeprofit)

            
    def position_size_calculator(self, balance, riskpct, signal, price, pipstoploss):
        if signal == 'buy':
            return round((((balance*riskpct)*price['ask']) / (pipstoploss/10000)))
        elif signal == 'sell':
            return -round((((balance*riskpct)*price['bid']) / (pipstoploss/10000)))

    
    def margin_requirement(self, units, marginpct):
        margin = units * marginpct
        if margin < 0:
            return -margin
        return margin