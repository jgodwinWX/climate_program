import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import urllib,urllib3
import requests
import json

from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta

# data settings
st.set_page_config(layout='wide')
st.title('Daily Temperature and Precipitation Data Browser')

# function for loading data
@st.cache
def load_data(station,request_type):
    column_names = ['Date','MaxT','MinT','Precip','Snow','SnowDepth']
    data = pd.read_csv('http://data.rcc-acis.org/StnData?sid=%s&sdate=por&edate=por&elems=1,2,4,10,11&output=csv' % station,skiprows=1,names=['Date','MaxT','MinT','Precip','Snow','SnowDepth'])
    data['Date'] = pd.to_datetime(data['Date'],format='%Y-%m-%d')
    for x in column_names[1:]:
        data[x] = pd.to_numeric(data[x], errors='coerce')
    return data
    
def monthNumbers(month,month_names):
    return [i for i, x in enumerate(month_names) if x==month][0]

# selection station location
station_list = [
    'Baton Rouge, LA','Dallas/Fort Worth, TX','Fairbanks, AK','San Jose, CA'
    ]
station_dict = {
    'Baton Rouge, LA':'BTRthr',
    'Dallas/Fort Worth, TX':'DFWthr',
    'Fairbanks, AK':'FAIthr',
    'San Jose, CA':'SJCthr'
    }
station_name = st.radio('Select Station: ',station_list)
station = station_dict[station_name]
    
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load the climate data
data_all = load_data(station,'observed')
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using streamlit.cache)")

# month and year selection
month_names = ['January','February','March','April','May','June','July','August','September','October','November','December']
month = st.radio('Select Month: ',month_names)
month_num = monthNumbers(month,month_names)+1
year = st.slider('Select Year: ',min_value=data_all['Date'].min().year,max_value=data_all['Date'].max().year,step=1,value=data_all['Date'].max().year)

# Buttons to go foward and backward in time (10 years, 1 year, 1 month, current)
if st.button("Current Month"):
    month_num = datetime.datetime.today().month
    month = datetime.datetime.today().strftime('%B')
    year = datetime.datetime.today().year
    
if st.button("Previous Month"):
    previous_month_date = datetime.datetime.today() + relativedelta(months=-1)
    month_num = previous_month_date.month
    month = previous_month_date.strftime('%B')
    year = previous_month_date.year

data = data_all[(data_all['Date'].dt.year==year)&(data_all['Date'].dt.month==month_num)]

# create figures based on user options
st.write('Select fields:')
fig = make_subplots(specs=[[{"secondary_y": True}]])
if st.checkbox('Maximum Temperatures'):
    fig.add_trace(go.Line(x=data['Date'],y=data['MaxT'],mode='lines+markers',line=dict(color="red"),name='High Temperature'),secondary_y=False)
if st.checkbox('Minimum Temperatures'):
    fig.add_trace(go.Line(x=data['Date'],y=data['MinT'],mode='lines+markers',line=dict(color="blue"),name='Low Temperature'),secondary_y=False)
if st.checkbox('Precipitation'):
    fig.add_trace(go.Bar(x=data['Date'],y=data['Precip'],marker=dict(color="green"),name='Precipitation'),secondary_y=True)
if st.checkbox('Snowfall'):
    fig.add_trace(go.Bar(x=data['Date'],y=data['Snow'],marker=dict(color="purple"),name='Snow'),secondary_y=True)
    
# plot aesthetics
fig.update_layout(
    title = '%s Daily Temperatures and Precipitation for %s %d' % (station_name,month,year),
    xaxis_title = 'Date'
    )
fig.update_yaxes(
    title_text='Temperature (F)',
    secondary_y=False
    )
fig.update_yaxes(
    title_text='Precipitation (in)',
    range = [0,10],
    secondary_y=True
    )

st.plotly_chart(fig,use_container_width=True)

# monthly summary

st.subheader('Raw data')
st.write(data)