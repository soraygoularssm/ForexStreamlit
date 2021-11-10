import oandapyV20.endpoints.instruments as instruments
import oandapyV20
accountID = "101-001-18208416-001"
access_token = "9fe4e91981ed9e165a46008938672d09-59fb28314aeb3ed897c9e00badaf90f9"
client = oandapyV20.API(access_token=access_token)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import streamlit as st

def get_data(symbol, timeframe, count):
    params = {"count": count, "granularity": timeframe}
    r = instruments.InstrumentsCandles(instrument=symbol, params=params)
    client.request(r)
    candles = r.response['candles']

    df = pd.json_normalize(candles)
    df['volume'] = df['volume'].astype('float64').dropna()
    df = df[['volume']]
    return df

pairs = ("EUR_USD", "EUR_GBP", "EUR_JPY", "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_NZD", "GBP_USD", "USD_JPY", "USD_CAD" , "AUD_USD", "USD_CHF", "NZD_USD","GBP_JPY", "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_NZD", "AUD_JPY", "CAD_JPY", "CHF_JPY", "NZD_JPY", "AUD_CAD", "AUD_CHF", "AUD_NZD", "CAD_CHF", "NZD_CAD", "NZD_CHF")
pair = st.selectbox('select a pair' , pairs)
timeframe = st.sidebar.select_slider('Select the timeframe',options=['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D'])
candles_count = st.sidebar.slider('Select the number of candles' , 25 , 250 , step=5)

df = get_data(pair,timeframe,candles_count)

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.bar(df.index, df['volume'])
st.pyplot(fig , True)