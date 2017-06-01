import config
import requests

class Portfolio:
    
    def __init__(self):
        #initialist balance, margin requirement, pull existing open trades.
        self.balance, self.currency, self.margin_available, self.margin_used = self.initialize_portfolio()


    def check_risk():
        #call risk module
        pass
    

    def view_open_trades():
        pass
    
    
    def open_trade(instrument, lotsize, stoploss, takeprofit):
        pass


    def account_summary(self):
        self.url = 'https://api-fxpractice.oanda.com/v3/accounts/{}'.format(config.account_id)
        self.headers = {'Authorization' : 'Bearer ' + config.access_token}
        req = requests.get(self.url, headers = self.headers)
        json = req.json()
        return json['account']


    def initialize_portfolio(self):
        summary = self.account_summary()
        return (summary['balance'], summary['currency'], summary['marginAvailable'], summary['marginUsed'])


    def update_margins(self):
        summary = self.account_summary()
        return (summary['marginAvailable'], summary['marginUsed'])

