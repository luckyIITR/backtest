import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
from finta import TA
from datetime import timedelta

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
# symbols = ["ICICIBANK.NS"]
for symbol in symbols:
    daily = yf.download( tickers = symbol,period = "100d",end = dt.datetime.now())
    daily.index = daily.index.tz_localize(None)
    daily.drop(["Adj Close",'Volume'],axis = 1,inplace = True)
    daily["pre_close"] = daily['Close'].shift(1)
    daily["pre_low"] = daily['Low'].shift(1)
    daily["pre_high"] = daily['High'].shift(1)
    piv=TA.PIVOT(daily)
    piv.dropna(inplace = True)
    data = yf.download( tickers = symbol,interval = "15m",period = "60d",end = dt.datetime.now())
    data.index = data.index.tz_localize(None)
    data.drop(["Adj Close",'Volume'],axis = 1,inplace = True)

    starting_date = data.index[0].date()
    piv = piv.loc[starting_date:,]
    daily = daily.loc[starting_date:,]

    percentchange=[]
    trade = {}
    for e in piv.index:
        today = data[data.index.date == e.date()].copy()
        today['pivot'] = piv.loc[e,"pivot"]
        today['s1'] = piv.loc[e,"s1"]
        today['s2'] = piv.loc[e,"s2"]
        today['s3'] = piv.loc[e,"s3"]
        today['s4'] = piv.loc[e,"s4"]
        today['r1'] = piv.loc[e,"r1"]
        today['r2'] = piv.loc[e,"r2"]
        today['r3'] = piv.loc[e,"r3"]
        today['r4'] = piv.loc[e,"r4"]
        pos=0
        
        #assingment
        openn15 = today.loc[today.index[0],"Open"]
        close15 = today.loc[today.index[0],"Close"]
        high15 = today.loc[today.index[0],"High"]
        low15 = today.loc[today.index[0],"Low"]
        r3 = today.loc[today.index[0],"r3"]
        s2 = today.loc[today.index[0],'s2']
        pre_high = daily.loc[[today.index[0].date()],'pre_high'][0]
        pre_low = daily.loc[[today.index[0].date()],'pre_low'][0]
        pre_close = daily.loc[[today.index[0].date()],'pre_close'][0]
        num = 0
        cd_buy = False
    #     cd_sell = False        
    #     conditions for buy
        cd_buy = (openn15 > pre_high) and (openn15 == low15) and openn15 < r3 #and today.loc[[today.index[0]+timedelta(minutes = 15)],'High'][0]> high15
        if cd_buy:
            trade[e] = {}
            for i in today.index:
                num +=1
                if cd_buy and pos==0:
                    pos = 1
                    bp = high15
                    continue 
                elif today.loc[i,"High"] > r3 and pos ==1 :
                    pos = 0
                    sp = r3
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
                    break
                elif today.loc[i,"Low"] < pre_close and pos == 1:
                    pos = 0
                    sp = pre_close
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
                    break
                if (num==today['Close'].count()-1 and pos==1):
                    pos = 0
                    sp = today.loc[i,"Open"]
                    pc=(sp/bp-1)*100
                    percentchange.append(pc)
                    trade[e]["buyed_at"] = bp
                    trade[e]['sold_at'] = sp 
                    trade[e]['pc'] = pc
    print(trade)
    
    gains=0
    ng=0
    losses=0
    nl=0
    totalR=1

    for i in percentchange:
        if(i>0):
            gains+=i
            ng+=1
        else:
            losses+=i
            nl+=1
        totalR=totalR*((i/100)+1)

    totalR=round((totalR-1)*100,2)

    if(ng>0):
        avgGain=gains/ng
        maxR=str(max(percentchange))
    else:
        avgGain=0
        maxR="undefined"

    if(nl>0):
        avgLoss=losses/nl
        maxL=str(min(percentchange))
        ratio=str(-avgGain/avgLoss)
    else:
        avgLoss=0
        maxL="undefined"
        ratio="inf"

    if(ng>0 or nl>0):
        battingAvg=ng/(ng+nl)
    else:
        battingAvg=0

    print()
    print(symbol)
    print("Batting Avg: "+ str(battingAvg))
    print("Gain/loss ratio: "+ ratio)
    print("Average Gain: "+ str(avgGain))
    print("Average Loss: "+ str(avgLoss))
    print("Max Return: "+ maxR)
    print("Max Loss: "+ maxL)
    print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
    #print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )
    print()
    overall.append(totalR)


gains=0
ng=0
losses=0
nl=0
totalR=1

for i in overall:
    if(i>0):
        gains+=i
        ng+=1
    else:
        losses+=i
        nl+=1
    totalR=totalR*((i/100)+1)

totalR=round((totalR-1)*100,2)

if(ng>0):
    avgGain=gains/ng
    maxR=str(max(overall))
else:
    avgGain=0
    maxR="undefined"

if(nl>0):
    avgLoss=losses/nl
    maxL=str(min(overall))
    ratio=str(-avgGain/avgLoss)
else:
    avgLoss=0
    maxL="undefined"
    ratio="inf"

if(ng>0 or nl>0):
    battingAvg=ng/(ng+nl)
else:
    battingAvg=0

print()
print(symbol)
print("Batting Avg: "+ str(battingAvg))
print("Gain/loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
#print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )
print()

