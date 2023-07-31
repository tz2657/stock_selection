# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 23:05:05 2023

@author: terry
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import datetime
import tushare as ts
from dateutil.relativedelta import relativedelta

token = '6f37b911fc7683af82358d6badbf1425a33afc9e291ba1cf975d9cfc'
pro = ts.pro_api(token)

## get today date YYYYMMDD
today_date = '20220505' ######pd.Timestamp('today').strftime("%Y%m%d")
today_datetime = datetime.datetime.strptime(today_date,'%Y%m%d')

months_ago_datetime = today_datetime + relativedelta(months=-6)  ## the datetime at 6 months ago
months_ago_date = pd.Timestamp(months_ago_datetime).strftime("%Y%m%d") #'20220705'
months_later_datetime = today_datetime + relativedelta(months=3)
months_later_date = pd.Timestamp(months_later_datetime).strftime("%Y%m%d") #'20220705'

stockdata = pro.stock_basic(list_status='L', fields='ts_code,symbol,name')
stockdata = stockdata[~stockdata.ts_code.str.startswith(('688','8'))] ## filter out 688 stocks

output_data = {'stock': [], 'today_min_price': []}   
output_df = pd.DataFrame(output_data)  

for index, row in stockdata.iterrows():
    ts_code = row['ts_code']
    df = pro.daily(ts_code=ts_code,start_date=months_ago_date,end_date=today_date)
    if len(df.index) == 0:
        continue
    recent_min_price = round(df['low'].min(),2)
    today_min_price = round(df.loc[df['trade_date']==today_date, 'low'],2)
    if len(today_min_price.index) == 0:
        continue
    today_min_price = today_min_price[0]
    str_today_min = str(today_min_price)
    
    ### consider later months
    df2 = pro.daily(ts_code=ts_code,start_date=today_date,end_date=months_later_date)
    if len(df.index) == 0:
        continue
    later_min_price = round(df2['low'].min(),2)
    ###
    
    if (today_min_price - recent_min_price) <= 0 and (later_min_price - today_min_price) < 0:  ## if today special min price is the lowest price in past 6 months:
        if len(str_today_min) == 4:
            if str_today_min[0] == str_today_min[2] and str_today_min[2] == str_today_min[3]:
                temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
                output_df = pd.concat([output_df, temp_df])
        elif len(str_today_min) == 5:
            if str_today_min[0] == str_today_min[1] and str_today_min[3] == str_today_min[4]:
                temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
                output_df = pd.concat([output_df, temp_df])
            elif str_today_min[0] == str_today_min[3] and str_today_min[2] == str_today_min[4]:
                temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
                output_df = pd.concat([output_df, temp_df])
            elif str_today_min[0] == str_today_min[4] and str_today_min[2] == str_today_min[3]:
                temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
                output_df = pd.concat([output_df, temp_df])
                


#maotai = pro.stock_basic(ts_code='600519.SH')


out_path = "C:\\Users\\terry\\Desktop\\counter_example_Special_Price_Selection_6month_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='Sheet1')
writer.save()




