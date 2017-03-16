# Oanda

This repository consists of modules to retrieve, analyse and trade financial instruments using the Oanda API.

Data:
Retrieve and store data into separate databases for each instrument.
Tables are created for each granularity level.
Data is retrieved using Oanda API credentials stored in the config.py file.
Data is stored using the SQL credentials stored in the config.py file.

Analysis:
Retrieve stored data from SQL database.
Perform analysis using Pandas library.
Data is retrieved using the SQL credentials stored in the config.py file.

Trade:
Uses the Oanda API to perform trade related operations.
Communicates with Oanda API using credentials stored in config.py.