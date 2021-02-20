import pandas as pd
# import numpy as np
import yfinance as yf
import datetime as dt
# from pandas_datareader import intra_data as pdr
from finta import TA
import os
import sqlite3
# from datetime import timedelta

dbd = r'F:\Database\15min_data'
#Connecting to Database
db = sqlite3.connect(os.path.join(dbd,"NSEEQ.db"))

def get_daily_data(symbol):
    daily = yf.download(tickers=symbol, start=dt.datetime(2019,9,1), end=dt.datetime.now())
    daily.index = daily.index.tz_localize(None)
    daily.drop(["Adj Close", 'Volume'], axis=1, inplace=True)
    daily["pre_close"] = daily['Close'].shift(1)
    daily["pre_low"] = daily['Low'].shift(1)
    daily["pre_high"] = daily['High'].shift(1)
    return daily

def get_intra_data(symbol):
    symbol_check = {'3MINDIA': 'MINDIA',
                    'BAJAJ-AUTO': 'BAJAJAUTO',
                    'J&KBANK': 'JKBANK',
                    'L&TFH': 'LTFH',
                    'M&MFIN': 'MMFIN',
                    'M&M': 'MM',
                    'NAM-INDIA': 'NAMINDIA',
                    'MCDOWELL-N': 'MCDOWELLN'}
    symbol = symbol[:-3]
    if symbol in list(symbol_check.keys()):
        symbol = symbol_check[symbol]

    df = pd.read_sql('''SELECT * FROM %s;''' % symbol, con=db)
    df.set_index('time', inplace=True)
    df.reset_index(inplace=True)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index("time", drop=True, inplace=True)
    df.index[0]
    df.drop(["oi", 'Volume'], axis=1, inplace=True)
    return df

def get_only_today_data(df,e):
    today = df[df.index.date == e.date()].copy()
    return today

def set_indicator(df,piv,e):
    df['pivot'] = piv.loc[e, "pivot"]
    df['s1'] = piv.loc[e, "s1"]
    df['s2'] = piv.loc[e, "s2"]
    df['s3'] = piv.loc[e, "s3"]
    df['s4'] = piv.loc[e, "s4"]
    df['r1'] = piv.loc[e, "r1"]
    df['r2'] = piv.loc[e, "r2"]
    df['r3'] = piv.loc[e, "r3"]
    df['r4'] = piv.loc[e, "r4"]
    return df

def calculate_everthing(percentchange):
    gains = 0
    ng = 0
    losses = 0
    nl = 0
    totalR = 1

    for i in percentchange:
        if (i > 0):
            gains += i
            ng += 1
        else:
            losses += i
            nl += 1
        totalR = totalR * ((i / 100) + 1)

    totalR = round((totalR - 1) * 100, 2)

    if (ng > 0):
        avgGain = gains / ng
        maxR = str(max(percentchange))
    else:
        avgGain = 0
        maxR = "undefined"

    if (nl > 0):
        avgLoss = losses / nl
        maxL = str(min(percentchange))
        ratio = str(-avgGain / avgLoss)
    else:
        avgLoss = 0
        maxL = "undefined"
        ratio = "inf"

    if (ng > 0 or nl > 0):
        battingAvg = ng / (ng + nl)
    else:
        battingAvg = 0

    print("Batting Avg: " + str(battingAvg))
    print("Gain/loss ratio: " + ratio)
    print("Average Gain: " + str(avgGain))
    print("Average Loss: " + str(avgLoss))
    print("Max Return: " + maxR)
    print("Max Loss: " + maxL)
    print("Total return over " + str(ng + nl) + " trades: " + str(totalR) + "%")
    # print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )
    print()

    return totalR


overall = []



symbols = ['ADANIPORTS.NS',
 'ASIANPAINT.NS',
 'AXISBANK.NS',
 'BAJAJ-AUTO.NS',
 'BAJAJFINSV.NS',
 'BAJFINANCE.NS',
 'BHARTIARTL.NS',
 'BPCL.NS',
 'BRITANNIA.NS',
 'CIPLA.NS',
 'COALINDIA.NS',
 'DIVISLAB.NS',
 'DRREDDY.NS',
 'EICHERMOT.NS',
 'GAIL.NS',
 'GRASIM.NS',
 'HCLTECH.NS',
 'HDFC.NS',
 'HDFCBANK.NS',
 'HDFCLIFE.NS',
 'HEROMOTOCO.NS',
 'HINDALCO.NS',
 'HINDUNILVR.NS',
 'ICICIBANK.NS',
 'INDUSINDBK.NS',
 'INFY.NS',
 'IOC.NS',
 'ITC.NS',
 'JSWSTEEL.NS',
 'KOTAKBANK.NS',
 'LT.NS',
 'M&M.NS',
 'MARUTI.NS',
 'NESTLEIND.NS',
 'NTPC.NS',
 'ONGC.NS',
 'POWERGRID.NS',
 'RELIANCE.NS',
 'SBILIFE.NS',
 'SBIN.NS',
 'SUNPHARMA.NS',
 'TATAMOTORS.NS',
 'TATASTEEL.NS',
 'TCS.NS',
 'TECHM.NS',
 'TITAN.NS',
 'ULTRACEMCO.NS',
 'UPL.NS',
 'WIPRO.NS']
# symbols = ["TATASTEEL.NS"]
# symbol = symbols[0]
for symbol in symbols:
    # getting EOD data and intraday data
    daily = get_daily_data(symbol)
    intra_data = get_intra_data(symbol)

    # getting pivot point in EOD data
    intra_data['atr']=TA.ATR(intra_data)

    # setting common starting_date for intraday data and EOD data / slicing data
    starting_date = dt.datetime(2020,2,3,0,0).date()
    daily = daily.loc[starting_date:,]
    intra_data = intra_data.loc[starting_date:,]
    '''note piv dataframe has has only pivot points only 
        and daily dataframe has EOD data and both has same starting date
        now intraday data and EOD data has same starting date set'''

    percentchange=[]
    trade = {}

    # since this backtest is only for intraday so we will go through day by day data and test our strategy
    for e in daily.index:     # looping in EOD data index
        # break
        # this will return intraday data for date e
        today = get_only_today_data(intra_data, e)
        if today.empty:
            continue
        # this will set_indicator to my intraday data
        # today = set_indicator(today, atr, e)

        pos=0
        
        #set intial data
        openn15 = today.loc[today.index[0], "Open"]
        close15 = today.loc[today.index[0], "Close"]
        high15 = today.loc[today.index[0], "High"]
        low15 = today.loc[today.index[0], "Low"]
        atr = today.loc[today.index[0], "atr"]
        pre_high = daily.loc[[today.index[0].date()], 'pre_high'][0]
        pre_low = daily.loc[[today.index[0].date()], 'pre_low'][0]
        pre_close = daily.loc[[today.index[0].date()], 'pre_close'][0]
        num = 0
        cd_buy = False
    #     cd_sell = False        
    #     conditions for buy
        cd_buy = (openn15 > pre_high) and (openn15 == low15)
        if cd_buy :
            buy_flag = 0
            for j in today.index:
                if j == today.index[0]: continue
                if high15 > today.loc[j,"High"] :
                    buy_flag = 1
            if not(buy_flag):
                continue


        if cd_buy:
            trade[e] = {}
            for i in today.index:
                num +=1
                if cd_buy and pos==0:
                    pos = 1
                    bp = high15
                    continue 
                elif today.loc[i, "High"] > (2*atr+high15) and pos == 1 :  # target reched
                    pos = 0
                    sp = (2*atr+high15)
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
                    break
                elif today.loc[i, "Low"] < pre_close*.98 and pos == 1: # hit sl
                    pos = 0
                    sp = pre_close*.98
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
                    break
                if (num==today['Close'].count() and pos==1):
                    pos = 0
                    sp = today.loc[i, "Open"]
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
            if pos == 1:
                print("Position still open NOTE !!!!!!!!!")
    print("************************************************************************************")
    print(symbol)
    print(trade)
    totalR = calculate_everthing(percentchange)
    overall.append(totalR)

print("#########################################################################################")
print("#########################################################################################")

overall_pnl = calculate_everthing(overall)
print(overall)
