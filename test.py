
import  pandas as  pd
import numpy as np

df=pd.read_csv('MW-NIFTY-200-08-Feb-2021.csv')
symbols = df['SYMBOL \n']
np.array(symbols[1:]) + ".NS"
