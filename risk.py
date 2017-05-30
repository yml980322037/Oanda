# # Currently building for USDJPY
import event
import analysis as an

class Risk:
    
    def __init__(self, instrument, riskpct):
        self.instrument = instrument
        self.riskpct = riskpct/100

    def calculate_risk(self, event_object):
        ev = event_object
        ev.type = 'trade'
        ev.sl, ev.tp = self.sl_tp_calculator(ev.df, event_object.signal)

        return ev

        
    def sl_tp_calculator(self, dataframe, signal):
        if signal == 'buy':
            price = dataframe.iloc[-1]['close']
            sl = min(dataframe[-6:]['low'])
            diff = (price - sl)
            tp = round(price + (diff * 1.5), 3)
            return (sl, tp)

        elif signal == 'sell':
            price = dataframe.iloc[-1]['close']
            sl = max(dataframe[-6:]['high'])
            diff = (sl - price)
            tp = round(price - (diff * 1.5), 3)
            return (sl, tp)
        else:
            return (0,0)
            
    def position_size_calculator(self, balance, riskpct, stoploss):
        return ((balance * (riskpct/100) / stoploss) / 0.00008817) #change to retrieve live rate on call
        
    def margin_requirement(self, lotsize, marginpct):
        return lotsize * (marginpct/100)
    
    def check_spread(self):
        return spread