import yfinance as yf
import datetime as dt
import pandas as pd


def get_intra_data(symbol):
    data = yf.download(tickers=symbol, interval="5m", period="1d", end=dt.datetime.now())
    data.index = data.index.tz_localize(None)
    data.drop(["Adj Close", 'Volume'], axis=1, inplace=True)
    return data

newdf = pd.DataFrame()
df = get_intra_data("SBIN.NS")
newdf['High'] = df['High']
newdf['Low'] = df['Low']

newdf['cummax'] = newdf['High'].cummax()
newdf['cummin'] = newdf['Low'].cummin()
newdf[['High','cummax','cummin']].plot()



