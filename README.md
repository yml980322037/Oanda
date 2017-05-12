# Oanda

This repository consists of modules to retrieve, analyse and trade financial instruments using the Oanda API.

Below is a summary of what the modules will consist of (Subject to change).

[Event]:
Event Class/Object:
Holds generated event information,

Event Queue Class:
Uses Queue class from collections library,
Add event to queue function,
Pop event from queue function,

[Source]:
Loop unless halted is returned in JSON dictionary from API,
Pull and store data into SQL database

Data [Handler]:
— Called to initiate cycle —
Pull latest data from SQL table, check latest row timestamp,
Adds to event queue, 
Include DataFrame object in event for Strategy object,
Include spread in events,
Outputs ’tick’ event (Dataframe)

Trading [Strategy]:
Receives ’tick’ event (Dataframe),
Outputs Long or Short signal to the update ePortfolio by Signal Event, 
Does not calculate quantity - Done by Risk module, 
Store common functions in [Analysis] (shared with [Risk]), 
Outputs ‘signal’ event (Buy/Sell, Dataframe)

[Risk] & Position Management:
Receives ’signal’ event (Buy/Sell, Dataframe), 
Store riskpct as constant - call risk object with parameter, 
Measure SL and TP, 
Calculate lot sizes, 
Check spread, 
Store common functions in [Analysis] (shared with [Strategy]), 
Outputs ‘trade’ event (riskpct, sl, tp, lot size, spread)

[Portfolio] & Order Management/Record:
Receives ‘trade’ event (riskpct, sl, tp, lot size, spread), 
Receives ‘fill’ event, 
Initialise with Account Data from API, 
Track positions/ Limit used margin, 
Only allow trade if margin & spread spec is met, 
Outputs ‘order’ event if appropriate

[Execution] Handling:
Receives ‘order’ event (sl, tp, lot size)
Separate Backtest & Live Execution Handlers, 
Send orders to broker by API, 
Receive ‘fill’ order and outputs to queue for [Portfolio]

