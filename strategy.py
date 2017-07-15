import event
import analysis as an
from datetime import timedelta



class MTL_Strategy:

	def __init__(self, ticker):
		self.ticker = ticker
		self.sma_st_lt = 0
		self.sma_st_lt_change_time = 0
		self.signal_sent_current_period = False

	def generate_signal(self, eventobject, open_trade):
		ev = eventobject
		ev.type = 'signal'
		signal = 'none'
		ev.signal = 'none'
		an.add_2_sma(ev.df, 7, 21)
		an.add_sma(ev.df, 70)
		an.compare_state(ev.df, 'SMA 7', 'SMA 21')
		
		# check if sma_mt_lt has changed
		if ev.df.iloc[-1]['SMA 7'] > ev.df.iloc[-1]['SMA 70']:
			if self.sma_st_lt != 'above':
				self.sma_st_lt = 'above'
				self.sma_st_lt_change_time = ev.time
				self.signal_sent_current_period = False
		elif ev.df.iloc[-1]['SMA 7'] < ev.df.iloc[-1]['SMA 70']:
			if self.sma_st_lt != 'below':
				self.sma_st_lt = 'below'
				self.sma_st_lt_change_time = ev.time
				self.signal_sent_current_period = False


		# Checks if the shorter term averages have crossed
		if ev.df.iloc[-1]['State'] != ev.df.iloc[-2]['State'] and ev.df.iloc[-1]['State'] != ev.df.iloc[-3]['State']:
			if ev.df.iloc[-1]['State'] == 'Above':
				signal = 'buy'
			elif ev.df.iloc[-1]['State'] == 'Below':
				signal = 'sell'
		else:
			ev.type = 'none'
			return ev

		if open_trade:
			if signal != 'none':
				ev.signal = signal
				return ev
			elif signal == 'none':
				ev.type = 'none'
				return ev


		if self.signal_sent_current_period == True:
			ev.type = 'none'
			return ev

		if ev.time - self.sma_st_lt_change_time > timedelta(minutes = 90):
			self.signal_sent_current_period = True
			ev.type = 'none'
			return ev


		# Checks if short term average matches longer term average (trend)
		if ev.df.iloc[-1]['SMA 7'] > ev.df.iloc[-1]['SMA 70'] and signal == 'buy':
			self.signal_sent_current_period = True
			ev.signal = 'buy'
			return ev
		elif ev.df.iloc[-1]['SMA 7'] < ev.df.iloc[-1]['SMA 70'] and signal == 'sell':
			self.signal_sent_current_period = True
			ev.signal = 'sell'
			return ev
		else:
			ev.type = 'none'
			return ev






class MA_ST_Strategy:

	def __init__(self, ticker):
		self.ticker = ticker

	def generate_signal(self, eventobject, open_trade):
		ev = eventobject
		ev.type = 'signal'
		signal = 'none'
		ev.signal = 'none'
		an.add_2_sma(ev.df, 7, 21)
		an.compare_state(ev.df, 'SMA 7', 'SMA 21')


		if ev.df.iloc[-1]['State'] != ev.df.iloc[-2]['State']:# and ev.df.iloc[-1]['State'] != ev.df.iloc[-3]['State']: l==17 p ==2
			if ev.df.iloc[-1]['State'] == 'Above':
				signal = 'Above'
			elif ev.df.iloc[-1]['State'] == 'Below':
				signal = 'Below'
		else:
			ev.type = 'none'
			return ev

		if open_trade == True:
			ev.signal = signal
			return ev

		long_term_df = ev.df_lt
		an.add_2_sma(long_term_df, 5, 10)
		an.compare_state(long_term_df, 'SMA 5', 'SMA 10')
		long_term_trend = long_term_df.iloc[-1]['State']
		if ev.df.iloc[-1]['State'] == long_term_trend:
			if signal == 'Above':
				ev.signal = 'buy'
				return ev
			elif signal == 'Below':
				ev.signal = 'sell'
				return ev
		else:
			ev.type = 'none'
			return ev

		


class MR_Strategy:

	def __init__(self, ticker):
		self.ticker = ticker

	def generate_signal(self, eventobject):
		ev = eventobject
		ev.type = 'signal'
		signal = 'none'
		ev.signal = 'none'
		an.add_2_sma(ev.df, 2, 15)
		an.add_state(ev.df, 2)
		ev.lt_sma = ev.df['SMA 15'].iloc[-1]

		if an.penultimate_bars_identical(ev.df, 4, 2) is not True:
			ev.type = 'none'
			return ev
		else:
			if ev.df['State 2'].iloc[-2] == 'Below':
				signal = 'buy'
			elif ev.df['State 2'].iloc[-2] == 'Above':
				signal = 'sell'

		last_bar_status = an.last_bar_status(ev.df, 2)

		if last_bar_status == 'Above' and signal == 'buy' and ev.df['close'][-2] > ev.df['open'][-2]:
			ev.signal = 'buy'
			return ev
		elif last_bar_status == 'Below' and signal == 'sell' and ev.df['open'][-2] > ev.df['close'][-2]:
			ev.signal = 'sell'
			return ev
		else:
			ev.type = 'none'
			return ev