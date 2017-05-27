# # Currently building for USDJPY

class risk:
    
    def __init__(self, instrument, riskpct):
        self.instrument = instrument
        self.riskpct = riskpct
        
    def sl_tp_calculator(dataframe):
        return 1
            
    def position_size_calculator(instrument, balance, riskpct, stoploss):
        return ((balance * (riskpct/100) / stoploss) / 0.00008817) #change to retrieve live rate on call
        
    def margin_requirement(lotsize, marginpct):
        return lotsize * (marginpct/100)
    
    def check_spread():
        return spread
    
    def order_event(order_request):
        return 1 # return event object with order data (long/short, orderamount, stoploss, takeprofit)
    
    def check_risk():
        pass

