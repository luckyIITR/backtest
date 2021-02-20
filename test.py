import pandas as pd
import os
import sqlite3


dbd = r'F:\Database\15min_data'
#Connecting to Database
db = sqlite3.connect(os.path.join(dbd,"NSEEQ.db"))
symbol = "SBIN"

df = pd.read_sql('''SELECT * FROM %s;''' %symbol, con=db)
df.set_index('time',inplace = True)
df.reset_index(inplace=True)
df['time']=pd.to_datetime(df['time'])
df.set_index("time",drop=True,inplace=True)
df.index[0]

db.close()


"sbin.ns"[:-3]
symbol_check = {'3MINDIA' : 'MINDIA',
                'BAJAJ-AUTO' : 'BAJAJAUTO',
                'J&KBANK' : 'JKBANK',
                'L&TFH' : 'LTFH',
                'M&MFIN' : 'MMFIN',
                'M&M' : 'MM',
                'NAM-INDIA' : 'NAMINDIA',
                'MCDOWELL-N' : 'MCDOWELLN'}