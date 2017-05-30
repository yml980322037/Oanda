# # Currently building for USDJPY
import event
import analysis as an

class Risk:
    
    def __init__(self, instrument, riskpct):
        self.instrument = instrument
        self.riskpct = riskpct/100

    def calculate_risk(self, event_object):
        ev = event.Event('trade')
        ev.df = event_object.df
        ev.sl = self.sl_tp_calculator(ev.df, event_object.signal)


        return ev

        
    def sl_tp_calculator(self, dataframe, signal):
        if signal == 'buy':
            return max(dataframe[-6:]['close'])
        elif signal == 'sell':
            return min(dataframe[-6:]['close'])
            
    def position_size_calculator(self, instrument, balance, riskpct, stoploss):
        return ((balance * (riskpct/100) / stoploss) / 0.00008817) #change to retrieve live rate on call
        
    def margin_requirement(self, lotsize, marginpct):
        return lotsize * (marginpct/100)
    
    def check_spread(self):
        return spread