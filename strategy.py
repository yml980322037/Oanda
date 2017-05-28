import event
import analysis as an

class Strategy:

	def generate_signal(self, eventobject):
		ev = event.event('signal')
		ev.df = eventobject.df
		an.add_2_sma_av(ev.df, 3, 7)
		an.add_state(ev.df, 'SMA3', 'SMA7')
		if ev.df.iloc[-1]['State'] == 'Above':
			ev.signal = 'buy'
		elif ev.df.iloc[-1]['State'] == 'Below':
			ev.signal = 'sell'
		return ev
