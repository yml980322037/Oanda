import event
import analysis as an
from datetime import timedelta

class Strategy:

	def generate_signal(self, eventobject):
		ev = eventobject
		ev.type = 'signal'
		signal = 'none'
		ev.signal = 'none'
		an.add_2_sma_av(ev.df, 3, 7)
		an.add_state(ev.df, 'SMA3', 'SMA7')


		if ev.df.iloc[-1]['State'] != ev.df.iloc[-2]['State']:
			if ev.df.iloc[-1]['State'] == 'Above':
				signal = 'Above'
			elif ev.df.iloc[-1]['State'] == 'Below':
				signal = 'Below'
		else:
			print('No new signal')
			ev.type = 'none'
			return ev



		if an.get_open_positions() == 0:
			three_hour_df = an.average_dataframe(an.selectlast('H3', ev.time, 7))
			an.add_2_sma_av(three_hour_df, 2, 7)
			an.add_state(three_hour_df, 'SMA2', 'SMA7')
			three_hour_trend = three_hour_df.iloc[-1]['State']
			ev.threehrdf = three_hour_df
			if ev.df.iloc[-1]['State'] == three_hour_trend:
				if signal == 'Above':
					ev.signal = 'buy'
				elif signal == 'Below':
					ev.signal = 'sell'
			else:
				print('No new signal')
				ev.type = 'none'
				return ev

		elif an.get_open_positions() != 0:
			last_fill = an.last_fill()
			if (ev.time - last_fill[0]) > timedelta(minutes = 30):
				if last_fill[1] > 0 and signal == 'Below':
						ev.type = 'close'
				if last_fill[1] < 0 and signal == 'Above':
						ev.type = 'close'
				else:
					print('Hold position')
					ev.type = 'none'
		
		else:
			print('Strategy error')

		return ev
