import config
import requests

class Portfolio:
    
    def __init__(self):
        #initialist balance, margin requirement, pull existing open trades.
        self.balance = None #Pull from API
    
    def view_open_trades():
        pass
    
    def check_risk():
        #call risk module
        pass
    
    def open_trade(instrument, lotsize, stoploss, takeprofit):
        pass

    def account_summary(self):
        self.url = 'https://api-fxpractice.oanda.com/v3/accounts/{}'.format(config.account_id)
        self.headers = {'Authorization' : 'Bearer ' + config.access_token}
        return requests.get(self.url, headers = self.headers)