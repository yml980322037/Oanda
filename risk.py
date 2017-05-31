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
        ev.pip_stop_loss = self.pip_stop_loss_calculator(ev.signal, ev.price, ev.sl)
        ev.units = self.position_size_calculator(500, self.riskpct, ev.signal, ev.price, ev.pip_stop_loss)
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
            return round((((balance*riskpct)*price['ask'])/(stoploss/100)))
        elif signal == 'sell':
            return round((((balance*riskpct)*price['bid'])/(stoploss/100)))

    def pip_stop_loss_calculator(self, signal, price, stoploss):
        if signal == 'buy':
            return round((price['ask'] - stoploss)*100, 2)
        elif signal == 'sell':
            return round((stoploss - price['bid'])*100, 2)

        
    def margin_requirement(self, units, marginpct):
        return units * marginpct