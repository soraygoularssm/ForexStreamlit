import oandapyV20.endpoints.instruments as instruments
import oandapyV20
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')


accountID = "101-001-18208416-001"
access_token = "9fe4e91981ed9e165a46008938672d09-59fb28314aeb3ed897c9e00badaf90f9"

client = oandapyV20.API(access_token=access_token)


def get_data(symbol, timeframe, count):
    params = {"count": count, "granularity": timeframe}
    r = instruments.InstrumentsCandles(instrument=symbol, params=params)
    client.request(r)
    candles = r.response['candles']

    df = pd.json_normalize(candles)
    df['high'] = df['mid.h'].astype('float64').dropna()
    df['low'] = df['mid.l'].astype('float64').dropna()
    df['open'] = df['mid.o'].astype('float64').dropna()
    df['close'] = df['mid.c'].astype('float64').dropna()
    df = df[['close']]
    return df


pairs = ["EUR_USD", "EUR_GBP", "EUR_JPY", "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_NZD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD",
                  "GBP_JPY", "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_NZD", "AUD_JPY", "CAD_JPY", "CHF_JPY", "NZD_JPY", "AUD_CAD", "AUD_CHF", "AUD_NZD", "CAD_CHF", "NZD_CAD", "NZD_CHF"]

currency_dict = {
    "EUR": ["EUR_USD", "EUR_GBP", "EUR_JPY", "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_NZD"],
    "USD": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"],
    "GBP": ["EUR_GBP", "GBP_USD", "GBP_JPY", "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_NZD"],
    "JPY": ["EUR_JPY", "GBP_JPY", "USD_JPY", "AUD_JPY", "CAD_JPY", "CHF_JPY", "NZD_JPY"],
    "AUD": ["EUR_AUD", "GBP_AUD", "AUD_USD", "AUD_JPY", "AUD_CAD", "AUD_CHF", "AUD_NZD"],
    "CAD": ["EUR_CAD", "AUD_CAD", "USD_CAD", "CAD_JPY", "GBP_CAD", "CAD_CHF", "NZD_CAD"],
    "CHF": ["EUR_CHF", "AUD_CHF", "USD_CHF", "CHF_JPY", "GBP_CHF", "CAD_CHF", "NZD_CHF"],
    "NZD": ["EUR_NZD", "AUD_NZD", "NZD_USD", "NZD_JPY", "GBP_NZD", "NZD_CHF", "NZD_CAD"]
}

pairs_data = {}

def changes(symbol):
    changes = [0 for _ in range(candles_count)]

    for pair in currency_dict[symbol]:
        df = pairs_data[pair]

        for candle in range(1, candles_count):
            last_price = df['close'][candle]
            first_price = df['close'][0]
            if(pair[:3] == symbol):
                change = ((last_price - first_price)*100)/first_price/7
            else:
                change = ((first_price - last_price)*100)/first_price/7

            changes[candle-1] += change

    return changes[:-1]


st.set_page_config(page_title="INDIVANALYZER", page_icon="🧊",
                   layout="wide", initial_sidebar_state="expanded")

symbols = ('EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD')
candles_count = st.sidebar.slider(
    'Select the number of candles', 50, 1500, step=10)
timeframe = st.sidebar.selectbox('Select the timeframe', [
                                 'M1', 'M5', 'M15', 'M30', 'H1', 'H4'])

if st.sidebar.button('Refresh'):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    st.write(f"last update: {current_time}")

progress_bar = st.progress(0)

for pair in pairs:
    df = get_data(pair, timeframe, candles_count)
    pairs_data[pair] = df
    if len(pairs_data) * 4 < 100:
        progress_bar.progress(len(pairs_data) * 4)
    else:
        progress_bar.progress(100)

progress_bar.empty()

currency_changes = []

col1, col2 = st.beta_columns(2)
for i in range(0, len(symbols)):
    if i % 2 == 0:
        change = changes(symbols[i])
        currency_changes.append(round(change[-1] - change[0], 2))
        col1.header(symbols[i])
        col1.line_chart(pd.DataFrame(change))
    else:
        change = changes(symbols[i])
        currency_changes.append(round(change[-1] - change[0], 2))
        col2.header(symbols[i])
        col2.line_chart(pd.DataFrame(change))

st.markdown("<hr /><br />", unsafe_allow_html=True,)

symbols_changes = []
for i in range(len(symbols)):
    symbol_change = [symbols[i] , currency_changes[i]]
    symbols_changes.append(symbol_change)
symbols_changes = sorted(symbols_changes, key=lambda x: x[1])

col1, col2 , col3 = st.beta_columns(3)

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.bar([item[0] for item in symbols_changes], [item[1] for item in symbols_changes])
col1.pyplot(fig , True)