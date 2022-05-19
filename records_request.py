import datetime
import pandas as pd
import requests

# function for building the dataframes for each record value set
def recordDfBuilder(data,valname):
    record_df = pd.DataFrame(data,columns=[valname,'Date'])
    record_df['Date'] = pd.to_datetime(record_df['Date'],format='%Y-%m-%d')
    record_df['Month'] = [x.month for x in record_df['Date']]
    record_df['Day'] = [x.day for x in record_df['Date']]
    year_name = 'Year_%s' % valname
    record_df[year_name] = [x.year for x in record_df['Date']]
    record_df.index = [datetime.datetime.strftime(x,'%Y-%m-%d')[-5:] for x in record_df['Date']]
    record_df[valname] = pd.to_numeric(record_df[valname], errors='coerce')
    return record_df

# function for posting requests to the ACIS API (documentation in comments below)
def recordRequester(station):
    #input_dict = {"sid":"DFWthr","sdate":"por","edate":"por","elems":[{"name":"maxt","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"}]}
    # JSON dictionary for ACIS: https://builder.rcc-acis.org/
    # how do this is described here: https://stackoverflow.com/questions/9733638/how-to-post-json-data-with-python-requests
    #input_dict = {"sid":"DFWthr","sdate":"por","edate":"por","elems":[{"name":"maxt","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"},{"name":"mint","interval":"dly","duration":1,"smry":{"add":"date","reduce":"min"},"smry_only":"1","groupby":"year"}]}
    input_dict = {"sid":station,"sdate":"por","edate":"por","elems":[
        {"name":"maxt","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"},
        {"name":"mint","interval":"dly","duration":1,"smry":{"add":"date","reduce":"min"},"smry_only":"1","groupby":"year"},
        {"name":"pcpn","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"},
        {"name":"snow","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"},
        {"name":"maxt","interval":"dly","duration":1,"smry":{"add":"date","reduce":"min"},"smry_only":"1","groupby":"year"},
        {"name":"mint","interval":"dly","duration":1,"smry":{"add":"date","reduce":"max"},"smry_only":"1","groupby":"year"}
        ]}
    # post request to ACIS API
    r = requests.post('http://data.rcc-acis.org/StnData',json=input_dict)
    # get a status code for any troubleshooting
    status_code = r.status_code
    return r,status_code

''' TEST CODE THAT JUST GRABS THE RECORDS AND PRINTS THEM 
# set the station ID and request the records
station = 'DFWthr'  # station to search
date = '05-19'      # date to search for daily record (mm-dd format)
r,status_code = recordRequester(station)

# get the lists containing the records and their dates
record_high_max = r.json()['smry'][0]
record_low_min = r.json()['smry'][1]
record_pcpn = r.json()['smry'][2]
record_snow = r.json()['smry'][3]
record_low_max = r.json()['smry'][4]
record_high_min = r.json()['smry'][5]

# build dataframes containing the calendar date, values, month code, and day codes
record_high_maxt_df = recordDfBuilder(record_high_max,'HighMaxT')   # Record high daily maximums
record_low_mint_df = recordDfBuilder(record_low_min,'LowMinT')      # Record low daily minimums
record_pcpn_df = recordDfBuilder(record_pcpn,'HighPCPN')            # Record high daily precipitation
record_snow_df = recordDfBuilder(record_snow,'HighSnow')            # Record high daily snow
record_low_maxt_df = recordDfBuilder(record_low_max,'LowMaxT')      # Record low daily maximums ("coldest highs")
record_high_mint_df = recordDfBuilder(record_high_min,'HighMinT')   # Record low daily maximums ("coldest highs")

# print the all-time records
print('All-time high maximum temperature: ')
print(record_high_maxt_df[record_high_maxt_df['HighMaxT']==record_high_maxt_df['HighMaxT'].max()])

print('\nAll-time low minimum temperature: ')
print(record_low_mint_df[record_low_mint_df['LowMinT']==record_low_mint_df['LowMinT'].min()])

print('\nAll-time high daily precipitation: ')
print(record_pcpn_df[record_pcpn_df['HighPCPN']==record_pcpn_df['HighPCPN'].max()])

print('\nAll-time high daily snow: ')
print(record_snow_df[record_snow_df['HighSnow']==record_snow_df['HighSnow'].max()])

print('\nAll-time low maximum temperature: ')
print(record_low_maxt_df[record_low_maxt_df['LowMaxT']==record_low_maxt_df['LowMaxT'].min()])

print('\nAll-time high minimum temperature: ')
print(record_high_mint_df[record_high_mint_df['HighMinT']==record_high_mint_df['HighMinT'].max()])

# print the daily records
print('-----------------------------------------------------------')
print('Daily records for %s:' % date)
print('\nRecord high:')
print(record_high_maxt_df[record_high_maxt_df.index==date])
print('\nRecord low:')
print(record_low_mint_df[record_low_mint_df.index==date])
print('\nRecord low maximum temperature:')
print(record_low_maxt_df[record_low_maxt_df.index==date])
print('\nRecord high minimum temperature:')
print(record_high_mint_df[record_high_mint_df.index==date])
print('\nGreatest Precipitation:')
print(record_pcpn_df[record_pcpn_df.index==date])
print('\nGreatest Snowfall:')
print(record_snow_df[record_snow_df.index==date])
'''