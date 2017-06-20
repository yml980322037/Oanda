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
				print('ST Signal A: ' + signal)
			elif ev.df.iloc[-1]['State'] == 'Below':
				signal = 'Below'
				print('ST Signal B: ' + signal)
		else:
			print('No new signal change')
			print(ev.df[-2:][['time', 'State']])
			print('SMA3: ',ev.df.iloc[-1]['SMA3'])
			print('SMA7: ',ev.df.iloc[-1]['SMA7'])
			print(ev.df)
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
					print('Open: both signal == Above')
					ev.signal = 'buy'
				elif signal == 'Below':
					print('Open: both signal == Below')
					ev.signal = 'sell'
			else:
				print('Both signals different')
				ev.type = 'none'
				return ev

		elif an.get_open_positions() != 0:
			last_fill = an.last_fill()
			print(last_fill)
			if (ev.time - last_fill[0]) > timedelta(minutes = 30):
				print('Over 30 mins ev.time: ' + str(ev.time) + '   last fill time: ' + str(last_fill[0]))
				if last_fill[1] > 0 and signal == 'Below':
						ev.type = 'close'
						print('close trade')
				elif last_fill[1] < 0 and signal == 'Above':
						ev.type = 'close'
						print('close trade')
				else:
					print('Hold position')
					ev.type = 'none'
			else:
				ev.type = 'none'
				print('Less than 30 mins')
		
		else:
			print('Strategy error')

		return ev
