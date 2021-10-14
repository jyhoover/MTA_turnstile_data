import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import requests
import altair as alt


def app():
    st.markdown('# Daily Stock Close Price Chart')
    st.markdown(
        'An interactive chart of daily stock closing prices using Streamlit and Altair')
    symbol = st.text_input('', 'IBM')
    date_range_picker = st.date_input(
        "pick the date range", [date(2021, 1, 4), date(2021, 9, 21)])
    datestr_format = '%Y-%m-%d'
    startdate = date_range_picker[0].strftime(datestr_format)
    enddate = date_range_picker[1].strftime(datestr_format)
    df = ticker(symbol).getdata()
    dfp = df.loc[(df.date >= startdate) & (
        df.date <= enddate)][['date', 'close']]
    dfp.rename({'close': 'close price'})
    # base = alt.Chart(dfp).mark_line().encode(
    #     x='date',
    #     y='close'
    # ).properties(
    #     width=600,
    #     height=200,
    #     title='close price of {}'.format(symbol)
    # )
    # st.altair_chart(base)
    brush = alt.selection(type='interval', encodings=['x'])

    base = alt.Chart(dfp).mark_area().encode(
        x='date:T',
        y='close:Q'
    ).properties(
        width=600,
        height=200
    )
    lower = base.properties(
        height=300
    ).add_selection(brush)

    st.altair_chart(lower)


class ticker:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol

    def getdata(self):
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        params = {'function': 'TIME_SERIES_DAILY',
                  'symbol': self.ticker_symbol,
                  'outputsize': 'full',
                  'apikey': 'X143BPH0G887CZ09'}
        url = 'https://www.alphavantage.co/query'
        data = requests.get(url, params).json()
        tsdata = data['Time Series (Daily)']
        ts_date = list(tsdata.keys())
        tsdata_list = np.zeros([len(ts_date), 5])
        columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
        columns_df = [x[3:] for x in columns]
        for i in range(len(ts_date)):
            for j in range(5):
                tsdata_list[i][j] = tsdata[ts_date[i]][columns[j]]

        df = pd.DataFrame(data=tsdata_list,
                          index=ts_date, columns=columns_df)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)
        df.date = pd.to_datetime(df.date)
        return df


if __name__ == '__main__':
    app()
