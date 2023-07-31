import pandas as pd
import datetime
import tushare as ts
from dateutil.relativedelta import relativedelta

token = '6f37b911fc7683af82358d6badbf1425a33afc9e291ba1cf975d9cfc'
pro = ts.pro_api(token)

## get today date YYYYMMDD
today_date = pd.Timestamp('today').strftime("%Y%m%d")  #### '20230109'
today_datetime = datetime.datetime.strptime(today_date,'%Y%m%d')

months_ago_datetime = today_datetime + relativedelta(months=-6)  ## the datetime at 6 months ago
months_ago_date = pd.Timestamp(months_ago_datetime).strftime("%Y%m%d") #'20220705'

stockdata = pro.stock_basic(list_status='L', fields='ts_code,symbol,name')
stockdata = stockdata[~stockdata.ts_code.str.startswith(('688','8'))] ## filter out 688 stocks

output_data = {'stock': [], 'today_min_price': []}   
output_df = pd.DataFrame(output_data)  

for index, row in stockdata.iterrows():
    ts_code = row['ts_code']
    df = pro.daily(ts_code=ts_code,trade_date=today_date) #start_date=today_date
    if len(df.index) == 0:
        continue
    #recent_min_price = round(df['low'].min(),2)
    today_min_price = round(row['low'],2)  #round(df.loc[df['trade_date']==today_date, 'low'],2)
    if len(today_min_price.index) == 0:
        continue
    today_min_price = today_min_price[0]
    str_today_min = str(today_min_price)
    
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


out_path = "C:\\Users\\terry\\Desktop\\Special_Price_Selection_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='6month_min')
writer.save()
writer.close()





