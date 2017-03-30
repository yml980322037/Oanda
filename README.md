# Oanda

This repository consists of modules to retrieve, analyse and trade financial instruments using the Oanda API.

Below is a summary of what the modules will consist of (Subject to change).

Data [Handler]:
Retrieves data from DB for live trade
or from SQL Query to DataFrame for Backtest, 
Adds to event queue, 
Include DataFrame object in event for Strategy object,
Include spread in event

Trading [Strategy]:
Event-driven, 
Outputs Long or Short signal to Portfolio by Signal Event, 
Does not calculate quantity - Done by Risk module
Store common functions in [Analysis]

[Portfolio] & Order Management/Record:
Event Handler/ Handle all events and keep record, 
Check FxTrade and others for record fields, 
Centre of Trading Program, 
Initialise with Account Data, 
Use Oanda Practice Account for Backtest, with API pull to Initialise Object,  
Track positions/ Limit used margin, 
Only allow trade if margin spec is met, 
Manage risk

[Risk] & Position Management:
Measure SL and TP, 
Calculate lot sizes, 
Check spread (as % to trade size)

[Execution] Handling:
Separate Backtest & Live Execution Handlers, 
Send orders to broker by API, 
Receive fill order

[Event]:
Event Class/Object:
Holds generated event information

Event Queue Class:
Uses Queue class from collections library
Add to queue function
Pop from queue function