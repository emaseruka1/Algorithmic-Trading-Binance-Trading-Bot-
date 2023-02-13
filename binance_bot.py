# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 16:41:32 2023

@author: Emmanuel
"""
import os

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from datetime import datetime, date, time, timedelta
import pandas as pd
import json
import requests
from datetime import datetime
now = datetime.now()
#import beepy

import pygsheets

path= "E:/JUPTYER CLASS WORK/emma-bot-377216-b89934ede92a.json"

authorising_access = pygsheets.authorize(service_account_file=path)

opened_worksheet=authorising_access.open_by_url('https://docs.google.com/spreadsheets/d/1r18TexWo9TuaA51Gv1O72mBN8aFDGK_a6v-Gr3FxXVs/edit#gid=0')
bot_worksheet=opened_worksheet[0]



today = date.today()
sell_strike =[-20]
buy_strike =[20]

#https://readthedocs.org/projects/python-binance/downloads/pdf/latest/
#https://github.com/PythonForForex/Binance-api-step-by-step-guide/blob/master/create_order.py
#https://python.plainenglish.io/how-to-download-trading-data-from-binance-with-python-21634af30195
#https://www.plus2net.com/python/pygsheets-append_table.php


key= '####'

secret= '####'

client = Client(key,secret)


lookback = today - timedelta(days=30)
today=today.strftime('%Y/%m/%d')
lookback =lookback.strftime('%Y/%m/%d')


symbol = "BTCBUSD"
interval= "1d"
klines = client.get_historical_klines(symbol, interval, lookback, today)


btc = pd.DataFrame(klines)
 # create colums name
btc.columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
btc= btc[['close_time','close']]
btc.index = [datetime.fromtimestamp(x/1000.0) for x in btc.close_time]
btc= btc[['close']]
max_price = pd.to_numeric(btc.max())
min_price = pd.to_numeric(btc.min())



price_key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCBUSD"
curr_price = requests.get(price_key)  
curr_price= curr_price.json()

curr_price=float(curr_price['price'])

below20 = ((curr_price - max_price)/max_price)*100 #Sell if below 20% from top
above20 = ((curr_price - min_price)/min_price)*100 #buy if above 20% from bottom
avail_usdt = client.get_asset_balance(asset='BUSD')
avail_usdt =float(avail_usdt['free'])


#Calculate possible buy coin quantity
buy_quantity = avail_usdt/curr_price

avail_btc = client.get_asset_balance(asset='BTC')
avail_btc = float(avail_btc['free'])


#Calculate possible sell coin quantity
sell_quantity = avail_btc


#used to check for our position
avail_btc_in_USDT = avail_btc*curr_price

#converting to list

avail_btc_in_USDT =[avail_btc_in_USDT]
avail_btc =[avail_btc]

position_indicator_buy=[1,now.strftime("%d/%m/%Y  %H:%M:%S"),curr_price,round(above20[0],3),round(below20[0],3)]
position_indicator_sell=[0,now.strftime("%d/%m/%Y  %H:%M:%S"),curr_price,round(above20[0],3),round(below20[0],3)]
position_indicator_NA=[-1,now.strftime("%d/%m/%Y  %H:%M:%S"),curr_price,round(above20[0],3),round(below20[0],3)]

if below20[0] <=sell_strike[0] and avail_btc_in_USDT[0] > avail_usdt[0]:
    #selling
        client.create_order(symbol=symbol,side='SELL',type ='LIMIT',price =curr_price ,quantity = round(sell_quantity,5),timeInForce='GTC')
        x=bot_worksheet.append_table(position_indicator_sell)
        #beep(sound='coin')
        print("sell")
        
        
elif above20[0] >= buy_strike[0] and avail_btc_in_USDT[0] < avail_usdt[0]:
    #buying
        client.create_order(symbol=symbol,side='BUY',type ='LIMIT',price =curr_price ,quantity = round(buy_quantity,5),timeInForce='GTC')
        y=bot_worksheet.append_table(position_indicator_buy)
        #beep(sound='coin')    
        print("buy")
        print()
        
        
else:
        z=bot_worksheet.append_table(position_indicator_NA)
        print("do nothing")
















