import config
import requests

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
        if self.pct_change < -3 or ev.spread > 2 or ev.margin_total > (balance * 0.3) :
            ev.type = 'none'
            return ev
        else:
            ev.type = 'order'
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
