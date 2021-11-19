import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import requests
import altair as alt
import geopandas
import folium
import dill
from streamlit_folium import folium_static


def app():
    st.markdown('# Fatastic Commuters and Where to Find Them')
    st.markdown(
        'An application that tells you where, when, and how many NYC subway commuters you are going to find')
    st.markdown("First, let's take a look of the past data")
    past_date = st.date_input(
        """Input a date in the past\n
            (between 2021-01-02 and 2021-07-16)""",
        value=pd.Timestamp('2021-02-01'),
        min_value=pd.Timestamp('2021-01-02'),
        max_value=pd.Timestamp('2021-07-16'))
    past_interval = st.selectbox(
        'Pick an interval',
        ('12 AM - 4 AM',
         '4 AM - 8 AM',
         '8 AM - 12 AM',
         '12 PM - 4 PM',
         '4 PM - 8 PM',
         '8 PM - 12 AM'))
    st.markdown(
        "(Feel free to drag or zoom at the map below. if you click on the bubble, you will see the stop's name.-)")
    past_interval_p = parse_interval(past_interval)
    datetimestr = str(past_date) + past_interval_p
    past_data(datetimestr)

    st.markdown("Now, let's take a look of the future")
    new_date = st.date_input(
        '''Input a date in the future\n
            (after 2021-07-17)''',
        min_value=pd.Timestamp('2021-07-17'))
    new_interval = st.selectbox(
        'Which interval are you interested?',
        ('12 AM - 4 AM',
         '4 AM - 8 AM',
         '8 AM - 12 AM',
         '12 PM - 4 PM',
         '4 PM - 8 PM',
         '8 PM - 12 AM'))

    time_info = (new_date, new_interval)
    predict_model(time_info)


def predict_model(time_info):
    date, interval = time_info

    with open('est_onehot_ridge.dill', 'rb') as f:
        est = dill.load(f)
    with open('dsl_geo.dill', 'rb') as g:
        dsl_geo = dill.load(g)
    with open('station_name.dill', 'rb') as p:
        station_name = dill.load(p)
    m_new = folium.Map(location=[40.754222, -73.984569],
                       tiles="OpenStreetMap", zoom_start=11)
    for stop in station_name:
        X = pd.DataFrame([[stop,
                           interval_code(interval),
                           date.weekday()]],
                         columns=['Station', 'interval_code', 'weekday_code'])
        y_pred = est.predict(X)[0]

        stop_loc = dsl_geo[dsl_geo['Stop_Name'] == stop.lower()]
        if len(stop_loc) == 0:
            continue
        folium.CircleMarker(
            location=[stop_loc.iloc[0]['GTFS_Latitude'],
                      stop_loc.iloc[0]['GTFS_Longitude']],
            popup=round(y_pred),
            radius=y_pred / 150,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m_new)

    folium_static(m_new)


def past_data(datetimestr):
    with open('df_geo.dill', 'rb') as f:
        df_geo = dill.load(f)

    df = df_geo[df_geo.Timegrp.str.contains(datetimestr)]

    m = folium.Map(location=[40.754222, -73.984569],
                   tiles="OpenStreetMap", zoom_start=11)
    for i in range(0, df.shape[0]):
        folium.CircleMarker(
            location=[df.iloc[i]['GTFS_Latitude'],
                      df.iloc[i]['GTFS_Longitude']],
            popup=df.iloc[i]['Station'],
            radius=float(df.iloc[i]['Exits_change']) / 150,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

    folium_static(m)


def parse_interval(past_interval):
    if past_interval == '12 AM - 4 AM':
        return(',')
    elif past_interval == '4 AM - 8 AM':
        return(' 04:00:00,')
    elif past_interval == '8 AM - 12 AM':
        return(' 08:00:00,')
    elif past_interval == '12 PM - 4 PM':
        return(' 12:00:00,')
    elif past_interval == '4 PM - 8 PM':
        return(' 16:00:00,')
    elif past_interval == '8 PM - 12 AM':
        return(' 20:00:00,')
    return('foo')


def interval_code(new_interval):
    if new_interval == '12 AM - 4 AM':
        return(0)
    elif new_interval == '4 AM - 8 AM':
        return(1)
    elif new_interval == '8 AM - 12 AM':
        return(2)
    elif new_interval == '12 PM - 4 PM':
        return(3)
    elif new_interval == '4 PM - 8 PM':
        return(4)
    elif new_interval == '8 PM - 12 AM':
        return(5)
    return('foo')


def warn(*args, **kwargs):
    pass


import warnings
warnings.warn = warn
if __name__ == '__main__':
    app()
