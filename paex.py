import streamlit as st
from scipy.signal import savgol_filter as smooth
import plotly.figure_factory as ff
import plotly.graph_objects as go
import talib as ta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import similaritymeasures
import requests

import oandapyV20
import oandapyV20.endpoints.instruments as instruments

accountID = "101-001-18208416-001"
access_token = "9fe4e91981ed9e165a46008938672d09-59fb28314aeb3ed897c9e00badaf90f9"

client = oandapyV20.API(access_token=access_token) 

candlestick_patterns = {
    'CDL2CROWS':'Two Crows',
    'CDL3BLACKCROWS':'Three Black Crows',
    'CDL3INSIDE':'Three Inside Up/Down',
    'CDL3LINESTRIKE':'Three-Line Strike',
    'CDL3OUTSIDE':'Three Outside Up/Down',
    'CDL3STARSINSOUTH':'Three Stars In The South',
    'CDL3WHITESOLDIERS':'Three Advancing White Soldiers',
    'CDLABANDONEDBABY':'Abandoned Baby',
    'CDLADVANCEBLOCK':'Advance Block',
    'CDLBELTHOLD':'Belt-hold',
    'CDLBREAKAWAY':'Breakaway',
    'CDLCLOSINGMARUBOZU':'Closing Marubozu',
    'CDLCONCEALBABYSWALL':'Concealing Baby Swallow',
    'CDLCOUNTERATTACK':'Counterattack',
    'CDLDARKCLOUDCOVER':'Dark Cloud Cover',
    'CDLDOJI':'Doji',
    'CDLDOJISTAR':'Doji Star',
    'CDLDRAGONFLYDOJI':'Dragonfly Doji',
    'CDLENGULFING':'Engulfing Pattern',
    'CDLEVENINGDOJISTAR':'Evening Doji Star',
    'CDLEVENINGSTAR':'Evening Star',
    'CDLGAPSIDESIDEWHITE':'Up/Down-gap side-by-side white lines',
    'CDLGRAVESTONEDOJI':'Gravestone Doji',
    'CDLHAMMER':'Hammer',
    'CDLHANGINGMAN':'Hanging Man',
    'CDLHARAMI':'Harami Pattern',
    'CDLHARAMICROSS':'Harami Cross Pattern',
    'CDLHIGHWAVE':'High-Wave Candle',
    'CDLHIKKAKE':'Hikkake Pattern',
    'CDLHIKKAKEMOD':'Modified Hikkake Pattern',
    'CDLHOMINGPIGEON':'Homing Pigeon',
    'CDLIDENTICAL3CROWS':'Identical Three Crows',
    'CDLINNECK':'In-Neck Pattern',
    'CDLINVERTEDHAMMER':'Inverted Hammer',
    'CDLKICKING':'Kicking',
    'CDLKICKINGBYLENGTH':'Kicking - bull/bear determined by the longer marubozu',
    'CDLLADDERBOTTOM':'Ladder Bottom',
    'CDLLONGLEGGEDDOJI':'Long Legged Doji',
    'CDLLONGLINE':'Long Line Candle',
    'CDLMARUBOZU':'Marubozu',
    'CDLMATCHINGLOW':'Matching Low',
    'CDLMATHOLD':'Mat Hold',
    'CDLMORNINGDOJISTAR':'Morning Doji Star',
    'CDLMORNINGSTAR':'Morning Star',
    'CDLONNECK':'On-Neck Pattern',
    'CDLPIERCING':'Piercing Pattern',
    'CDLRICKSHAWMAN':'Rickshaw Man',
    'CDLRISEFALL3METHODS':'Rising/Falling Three Methods',
    'CDLSEPARATINGLINES':'Separating Lines',
    'CDLSHOOTINGSTAR':'Shooting Star',
    'CDLSHORTLINE':'Short Line Candle',
    'CDLSPINNINGTOP':'Spinning Top',
    'CDLSTALLEDPATTERN':'Stalled Pattern',
    'CDLSTICKSANDWICH':'Stick Sandwich',
    'CDLTAKURI':'Takuri (Dragonfly Doji with very long lower shadow)',
    'CDLTASUKIGAP':'Tasuki Gap',
    'CDLTHRUSTING':'Thrusting Pattern',
    'CDLTRISTAR':'Tristar Pattern',
    'CDLUNIQUE3RIVER':'Unique 3 River',
    'CDLUPSIDEGAP2CROWS':'Upside Gap Two Crows',
    'CDLXSIDEGAP3METHODS':'Upside/Downside Gap Three Methods'
}

# st.set_page_config(page_title="PAEX",page_icon="🧊",layout="wide",initial_sidebar_state="expanded")
def get_data(count):
    params = {"count": count ,"granularity": timeframe}
    r = instruments.InstrumentsCandles(instrument=symbol,params=params)
    client.request(r)
    candles = r.response['candles']

    df = pd.json_normalize(candles)

    return df

def get_pattern(candles_count , timeframe , symbol , df):
    open = df['mid.o'].astype('float64') 
    close = df['mid.c'].astype('float64') 
    high = df['mid.h'].astype('float64') 
    low = df['mid.l'].astype('float64') 
    volume = df['volume'].astype('float64')

    found_pattern_candle_index = 0
    last_pattern_code = ''
    last_pattern_name = ''
    last_pattern_signal = 0

    for pattern in candlestick_patterns:
        pattern_function = getattr(ta , pattern)
        num = pattern_function(open,high,low,close)
        if num[num != 0].empty == False:
            for k ,v in num[num != 0].items():
                if k > found_pattern_candle_index:
                    found_pattern_candle_index = k
                    last_pattern_signal = v
                    last_pattern_code = pattern
                    last_pattern_name = candlestick_patterns[pattern]
    
    st.subheader(str(candles_count - found_pattern_candle_index) + " candles back " + last_pattern_name + " found")
    if last_pattern_signal == 100:
        st.markdown('<h4 style="color:green;">BUY SIGNAL</h4>', unsafe_allow_html=True)
    elif last_pattern_signal == 200:
        st.markdown('<h4 style="color:green;">STRONG BUY SIGNAL</h4>', unsafe_allow_html=True)
    elif last_pattern_signal == -100:
        st.markdown('<h4 style="color:red;">SELL SIGNAL</h4>', unsafe_allow_html=True)
    elif last_pattern_signal == -200:
        st.markdown('<h4 style="color:red;">STRONG SELL SIGNAL</h4>', unsafe_allow_html=True)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=open,
                high=high,
                low=low,
                close=close,
                name=symbol)])
    
    fig.update_layout(
        title=symbol+ ' ' + timeframe + ' Chart',
        xaxis_title="candles count",
        yaxis_title="Price ($)",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="black"
        )
    )
    
    st.plotly_chart(fig,  use_container_width=True)

def get_support_resistance(df):
    close = df['mid.c'].astype('float64')

    data = close.to_numpy()
    
    def support(ltp, n):
        """
        This function takes a numpy array of last traded price
        and returns a list of support and resistance levels
        respectively. n is the number of entries to be scanned.
        """

        # converting n to a nearest even number
        if n % 2 != 0:
            n += 1

        n_ltp = ltp.shape[0]

        # smoothening the curve
        ltp_s = smooth(ltp, (n + 1), 3)

        # taking a simple derivative
        ltp_d = np.zeros(n_ltp)
        ltp_d[1:] = np.subtract(ltp_s[1:], ltp_s[:-1])

        resistance = []
        support = []

        for i in range(n_ltp - n):
            arr_sl = ltp_d[i:(i + n)]
            first = arr_sl[:(n // 2)]  # first half
            last = arr_sl[(n // 2):]  # second half

            r_1 = np.sum(first > 0)
            r_2 = np.sum(last < 0)

            s_1 = np.sum(first < 0)
            s_2 = np.sum(last > 0)

            # local maxima detection
            if (r_1 == (n // 2)) and (r_2 == (n // 2)):
                resistance.append(ltp[i + ((n // 2) - 1)])

            # local minima detection
            if (s_1 == (n // 2)) and (s_2 == (n // 2)):
                support.append(ltp[i + ((n // 2) - 1)])

        return support

    sup = support(data, 20)

    def resistance(ltp, n):
        """
        This function takes a numpy array of last traded price
        and returns a list of support and resistance levels
        respectively. n is the number of entries to be scanned.
        """

        # converting n to a nearest even number
        if n % 2 != 0:
            n += 1

        n_ltp = ltp.shape[0]

        # smoothening the curve
        ltp_s = smooth(ltp, (n + 1), 3)

        # taking a simple derivative
        ltp_d = np.zeros(n_ltp)
        ltp_d[1:] = np.subtract(ltp_s[1:], ltp_s[:-1])

        resistance = []
        support = []

        for i in range(n_ltp - n):
            arr_sl = ltp_d[i:(i + n)]
            first = arr_sl[:(n // 2)]  # first half
            last = arr_sl[(n // 2):]  # second half

            r_1 = np.sum(first > 0)
            r_2 = np.sum(last < 0)

            s_1 = np.sum(first < 0)
            s_2 = np.sum(last > 0)

            # local maxima detection
            if (r_1 == (n // 2)) and (r_2 == (n // 2)):
                resistance.append(ltp[i + ((n // 2) - 1)])

            # local minima detection
            if (s_1 == (n // 2)) and (s_2 == (n // 2)):
                support.append(ltp[i + ((n // 2) - 1)])

        return resistance

    res = resistance(data, 20)

    ycoords_sup = sup
    ycoords_res = res
    # colors for the lines
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    for ycs,ycr,c in zip(ycoords_sup,ycoords_res,colors):
        plt.axhline(y=ycs, label='support at y = {}'.format(ycs), c=c)
        plt.axhline(y=ycr, label='resistance at y = {}'.format(ycr), c=c)
    close.plot(figsize=(8,4),grid=True)

    plt.xticks(rotation=90)
    # plt.legend()
    st.pyplot(plt)

def get_similar_pattern():
    df_main = get_data(5000)

    close = df['mid.c'].astype('float64')
    sim_vals = []

    for i in range(5000 - (2*candles_count)):
        close2 = df_main['mid.c'].astype('float64')[i:i + candles_count]
        # smooth_close2 = smooth(close2 , 9 , 3)
        sim_value1 = similaritymeasures.frechet_dist(np.array([df.index, close]), np.array([df.index, close2]))
        sim_value2 = similaritymeasures.curve_length_measure(np.array([df.index, close]), np.array([df.index, close2]))
        sim_value3 , d = similaritymeasures.dtw(np.array([df.index, close]), np.array([df.index, close2]))
        sim_value4 = similaritymeasures.pcm(np.array([df.index, close]), np.array([df.index, close2]))
        sim_value5 = similaritymeasures.area_between_two_curves(np.array([df.index, close]), np.array([df.index, close2]))
        sim_vals.append([i,sim_value1+sim_value2+sim_value3+sim_value4 + sim_value5])

    most_simillar_indexe = 0
    similarity_measures = 1000

    for i in sim_vals:
        if i[1] < similarity_measures: 
            similarity_measures = i[1]
            most_simillar_indexe = i[0]

    st.text("similarity number: " + str(similarity_measures) + " (less is better)")

    sim_close = df_main['mid.c'].astype('float64')[most_simillar_indexe : most_simillar_indexe + candles_count + predicted_candles_count]
    sim_smooth_close = smooth(sim_close , 9 , 3)

    plt.plot([i for i in range(len(df.index) + predicted_candles_count)] , sim_close)
    st.pyplot(plt)

st.title('PriceAction EXpert')

symbol = st.sidebar.selectbox('Select a currency pair',(    'XAU_USD' , 'EUR_USD' , 'CAD_JPY' , 'GBP_USD' , 'EUR_GBP', 'GBP_JPY' , 'AUD_CAD' , 'AUD_CHF'))
timeframe = st.sidebar.select_slider('Select the timeframe',options=['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D' , 'W'])
candles_count = st.sidebar.slider('Select the number of candles' , 25 , 250 , step=5)
predicted_candles_count = st.sidebar.slider('Select the number of future candles' , 20 , 150 , step=10)

df = get_data(candles_count)

get_pattern(candles_count,timeframe,symbol , df)

get_support_resistance(df)

get_similar_pattern()