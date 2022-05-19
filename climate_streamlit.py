import calendar
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta

from records_request import recordDfBuilder,recordRequester

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

# get the daily records
r,record_status_code = recordRequester(station)
record_high_max = r.json()['smry'][0]
record_low_min = r.json()['smry'][1]
record_pcpn = r.json()['smry'][2]
record_snow = r.json()['smry'][3]
record_low_max = r.json()['smry'][4]
record_high_min = r.json()['smry'][5]

record_high_maxt_df = recordDfBuilder(record_high_max,'HighMaxT')   # Record high daily maximums
record_low_mint_df = recordDfBuilder(record_low_min,'LowMinT')      # Record low daily minimums
record_pcpn_df = recordDfBuilder(record_pcpn,'HighPCPN')            # Record high daily precipitation
record_snow_df = recordDfBuilder(record_snow,'HighSnow')            # Record high daily snow
record_low_maxt_df = recordDfBuilder(record_low_max,'LowMaxT')      # Record low daily maximums ("coldest highs")
record_high_mint_df = recordDfBuilder(record_high_min,'HighMinT')   # Record low daily maximums ("coldest highs")

# do a bunch of merging to make one master daily records dateframe
record_list = [record_high_maxt_df,record_low_mint_df,record_pcpn_df,record_snow_df,record_low_maxt_df,record_high_mint_df]
for ix,x in enumerate(record_list):
    if ix == 0:
        records = record_high_maxt_df.merge(record_low_mint_df,left_index=True,right_index=True)
    elif ix < len(record_list)-1:
        records = records.merge(record_list[ix+1],left_index=True,right_index=True)
    else:
        records = records.drop(labels=['Date_x','Month_x','Day_x','Date_y','Month_y','Day_y'],axis=1)
        records['Month'] = records.index.get_level_values(0).str[0:2]
        records['Day'] = records.index.get_level_values(0).str[3:5]
        records['Month'] = pd.to_numeric(records['Month'], errors='coerce')
        records['Day'] = pd.to_numeric(records['Day'], errors='coerce')

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
data['Day'] = [x.day for x in data['Date']]

# filter down the daily records to the month we are interested in
records_filtered = records[records['Month']==month_num]

# create figures based on user options
st.write('Select fields:')
fig = make_subplots(specs=[[{"secondary_y": True}]])
if st.checkbox('Maximum Temperatures'):
    fig.add_trace(go.Line(
        x=data['Day'],
        y=data['MaxT'],
        customdata=[datetime.datetime.strftime(x,'%Y-%m-%d') for x in data['Date']],
        mode='lines+markers',
        line=dict(color="red",width=3),
        name='Observed High Temperature'),
        secondary_y=False)
    fig.add_trace(go.Line(
        x=records_filtered['Day'],
        y=records_filtered['HighMaxT'],
        customdata=records_filtered['Year_HighMaxT'],
        mode='lines',
        line=dict(color="red",width=1),
        name='Record High Temperature',xaxis='x2'),
        secondary_y=False
        )

if st.checkbox('Minimum Temperatures'):
    fig.add_trace(go.Line(
        x=data['Day'],
        y=data['MinT'],
        customdata=[datetime.datetime.strftime(x,'%Y-%m-%d') for x in data['Date']],
        mode='lines+markers',
        line=dict(color="blue",width=3),
        name='Observed Low Temperature'),
        secondary_y=False)
    fig.add_trace(go.Line(
        x=records_filtered['Day'],
        y=records_filtered['LowMinT'],
        customdata=records_filtered['Year_LowMinT'],
        mode='lines',line=dict(color="blue",width=1),
        name='Record Low Temperature'),
        secondary_y=False)
    
if st.checkbox('Precipitation'):
    fig.add_trace(go.Bar(
        x=data['Day'],
        y=data['Precip'],
        marker=dict(color="green"),
        name='Precipitation'),
        secondary_y=True)
    
if st.checkbox('Snowfall'):
    fig.add_trace(go.Bar(
        x=data['Day'],
        y=data['Snow'],
        marker=dict(color="purple"),
        name='Snow'),
        secondary_y=True)
    
# plot aesthetics
fig.update_layout(
    title = '%s Daily Temperatures and Precipitation for %s %d' % (station_name,month,year),
    xaxis_title = 'Day of Month',
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
fig.update_traces(
    hovertemplate="<br>".join([
        'Date: %{customdata}',
        'Temperature: %{y}'
        ])
    )

st.plotly_chart(fig,use_container_width=True)

# monthly summary

st.subheader('Daily Observed Values for %s %s' % (month,year))
st.write(data)
st.subheader('Record Values for the month of %s' % month)

st.write(records_filtered.drop(labels=['Month','Day','Fake Date Str','Fake Date'],axis=1))