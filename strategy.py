import event
import analysis as an

class Strategy:

	def generate_signal(self, eventobject):
		ev = event.Event('signal')
		ev.df = eventobject.df
		an.add_2_sma_av(ev.df, 3, 7)
		an.add_state(ev.df, 'SMA3', 'SMA7')

		three_hour_df = an.average_dataframe(an.selectlast('H3', ev.time, 7))
		an.add_2_sma_av(three_hour_df, 3, 7)
		an.add_state(three_hour_df, 'SMA3', 'SMA7')
		three_hour_trend = three_hour_df.iloc[-1]['State']


		if ev.df.iloc[-1]['State'] != ev.df.iloc[-2]['State'] and ev.df.iloc[-1]['State'] == three_hour_trend:
			if ev.df.iloc[-1]['State'] == 'Above':
				ev.signal = 'buy'
			elif ev.df.iloc[-1]['State'] == 'Below':
				ev.signal = 'sell'
		else:
			ev.signal = 'none'

		return ev
