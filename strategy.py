import event
import analysis as an
from datetime import timedelta

class MA_Strategy:

	def __init__(self, ticker):
		self.ticker = ticker
		self.sma_st_lt = 0
		self.sma_st_lt_change_time = 0
		self.signal_sent_current_period = False
		self.latest_signal = 'none'
		self.latest_signal_countdown = 0

	def generate_signal(self, eventobject, open_trade):
		ev = eventobject
		ev.type = 'signal'
		signal = 'none'
		ev.signal = 'none'
		an.add_sma(ev.df, 20)
		an.add_2_sma(ev.df, 5, 10)
		an.compare_state(ev.df, 'SMA 5', 'SMA 10')

		# check if sma_mt_lt has changed
		if ev.df.iloc[-1]['SMA 5'] > ev.df.iloc[-1]['SMA 20']:
			if self.sma_st_lt != 'Above':
				print('Switched to Above')
				self.sma_st_lt = 'Above'
				self.sma_st_lt_change_time = ev.time
				self.signal_sent_current_period = False
		elif ev.df.iloc[-1]['SMA 5'] < ev.df.iloc[-1]['SMA 20']:
			if self.sma_st_lt != 'Below':
				print('Switched to Below')
				self.sma_st_lt = 'Below'
				self.sma_st_lt_change_time = ev.time
				self.signal_sent_current_period = False

		if self.signal_sent_current_period == True:
			ev.type = 'none'
			return ev

		if self.latest_signal_countdown > 0 and self.latest_signal == self.sma_st_lt:
			self.latest_signal_countdown = 0
			self.signal_sent_current_period = True
			if self.latest_signal == 'Above':
				ev.signal = 'buy'
				return ev
			elif self.latest_signal == 'Below':
				ev.signal = 'sell'
				return ev
		else:
			self.latest_signal_countdown -= 1



		'''
		if ev.time - self.sma_st_lt_change_time > timedelta(hours = 10):
			self.signal_sent_current_period = True
			print('Too long between switch')
			ev.type = 'none'
			return ev
		
		'''

		if ev.df.iloc[-1]['State'] != ev.df.iloc[-2]['State']:
			if ev.df.iloc[-1]['State'] == 'Above' and ev.df.iloc[-1]['State'] == self.sma_st_lt:
				self.signal_sent_current_period = True
				self.latest_signal_countdown = 0
				ev.signal = 'buy'
				print('buy')
				return ev
			elif ev.df.iloc[-1]['State'] == 'Below' and ev.df.iloc[-1]['State'] == self.sma_st_lt:
				self.signal_sent_current_period = True
				self.latest_signal_countdown = 0
				ev.signal = 'sell'
				print('sell')
				return ev
			elif ev.df.iloc[-1]['State'] != self.sma_st_lt:
				print('sig different')
				self.latest_signal = ev.df.iloc[-1]['State']
				self.latest_signal_countdown = 3
				ev.type = 'none'
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