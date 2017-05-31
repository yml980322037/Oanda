# # Currently building for USDJPY
import event
import analysis as an

class Risk:
    
    def __init__(self, instrument, riskpct, marginpct):
        self.instrument = instrument
        self.riskpct = riskpct/100
        self.marginpct = marginpct/100

    def calculate_risk(self, event_object):
        ev = event_object
        ev.type = 'trade'
        ev.sl, ev.tp = self.sl_tp_calculator(ev.df, event_object.signal)
        ev.units = self.position_size_calculator(500, self.riskpct, ev.signal, ev.price, ev.sl)
        ev.margin = self.margin_requirement(ev.units, self.marginpct)

        return ev

        
    def sl_tp_calculator(self, dataframe, signal):
        if signal == 'buy':
            price = dataframe.iloc[-1]['close']
            sl = round(min(dataframe[-6:]['low']), 3)
            diff = (price - sl)
            tp = round(price + (diff * 1.5), 3)
            return (sl, tp)

        elif signal == 'sell':
            price = dataframe.iloc[-1]['close']
            sl = round(max(dataframe[-6:]['high']), 3)
            diff = (sl - price)
            tp = round(price - (diff * 1.5), 3)
            return (sl, tp)
        else:
            return (0,0)

            
    def position_size_calculator(self, balance, riskpct, signal, price, stoploss):
        if signal == 'buy':
            pipstoploss = round(price['ask'] - stoploss, 2)
            return round((((balance*riskpct)*price['ask'])/pipstoploss))
        elif signal == 'sell':
            pipstoploss = round(stoploss - price['bid'], 2)
            return round((((balance*riskpct)*price['bid'])/pipstoploss))

        
    def margin_requirement(self, units, marginpct):
        return units * marginpct