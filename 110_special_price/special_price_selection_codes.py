
## This is a personal project about automatic stock selection based on daily market data
import pandas as pd
import datetime
import tushare as ts
from dateutil.relativedelta import relativedelta


#token = '6f37b911fc7683af82358d6badbf1425a33afc9e291ba1cf975d9cfc' ## token of Tianhao
token = '7bc32e665d0c65878fd74a16f20ca6092e83c4b1ff1fd01c7c2ac3b3' ## token of Zhihua
#token = 'd388698a64fd19ed82052e7fa266578398cf1d5ffce7543838821b65' ## token of 163 mail

pro = ts.pro_api(token)



def check_special_number(str_number):
    if len(str_number) == 4:
        if str_number[0] == str_number[2] and str_number[2] == str_number[3]:
            return True
        elif str_number[0] == str_number[3] and str_number[2] != '.':
            return True
        else: 
            return False
    elif len(str_number) == 5:
        if str_number[0] == str_number[1] and str_number[3] == str_number[4]:
            return True
        elif str_number[0] == str_number[3] and str_number[1] == str_number[4]:
            return True
        elif str_number[0] == str_number[4] and str_number[1] == str_number[3]:
            return True
        else:
            return False
    else:
        print('price is not 3 or 4 digit')
        print(str_number)
        return False
    
    
    
## get today date YYYYMMDD
today_date = pd.Timestamp('today').strftime("%Y%m%d")
today_datetime = datetime.datetime.strptime(today_date,'%Y%m%d')

months_ago_datetime6 = today_datetime + relativedelta(months=-6)  ## the datetime at 6 months ago
months_ago_date6 = pd.Timestamp(months_ago_datetime6).strftime("%Y%m%d") #'20220705'
months_ago_datetime3 = today_datetime + relativedelta(months=-3)
months_ago_date3 = pd.Timestamp(months_ago_datetime3).strftime("%Y%m%d") #'20220705'
#months_ago_datetime1 = today_datetime + relativedelta(months=-1) 
#months_ago_date1 = pd.Timestamp(months_ago_datetime1).strftime("%Y%m%d")

stockdata = pro.stock_basic(list_status='L', fields='ts_code,symbol,name')
stockdata = stockdata[~stockdata.ts_code.str.startswith(('688','8','39','2','1'))] ## filter out 688 stocks

output_data = {'stock': [], 'today_min_price': []}   
output_df = pd.DataFrame(output_data)
output_df2 = pd.DataFrame(output_data)
#output_df3 = pd.DataFrame(output_data)


for index, row in stockdata.iterrows():
    ts_code = row['ts_code']
    df = pro.daily(ts_code=ts_code,start_date=months_ago_date6,end_date=today_date)
    df2 = df[df['trade_date'] >= months_ago_date3]
    #df3 = pro.daily(ts_code=ts_code,start_date=months_ago_date1,end_date=today_date)
    if len(df.index) == 0 or df['close'].values[1] >= 100:
        continue
    recent_min_price6 = round(df['low'].min(),2)
    recent_min_price3 = round(df2['low'].min(),2)
    #recent_min_price1 = round(df3['low'].min(),2)
    today_min_price = round(df2.at[0, "low"],2)    
    #today_min_price = round(df3.loc[df3['trade_date']==today_date, 'low'],2)
    
    #if len(today_min_price.index) == 0 or len(today_min_price.index) >= 2:
        #continue
    #today_min_price = today_min_price.iloc[0]
    
    str_today_min = str(today_min_price)
    
    if today_min_price - recent_min_price6 <= 0.05 and today_min_price < 100:  ## if today special min price is the lowest price in past 6 months:
        if check_special_number(str_today_min) is True:
            temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
            print("Congratulations! special " + ts_code + " " + str(today_min_price))
            output_df = pd.concat([output_df, temp_df])
    elif today_min_price - recent_min_price3 <= 0.05 and today_min_price < 100:
        if check_special_number(str_today_min) is True:
            temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
            print("Congratulations! special " + ts_code + " " + str(today_min_price))
            output_df2 = pd.concat([output_df2, temp_df])
    # elif today_min_price - recent_min_price1 <= 0 and today_min_price < 100:
    #     if check_special_number(str_today_min) is True:
    #         temp_df = pd.DataFrame({"stock":[ts_code], "today_min_price":[today_min_price]})
    #         print(temp_df)
    #         output_df3 = pd.concat([output_df3, temp_df])
    else:
        print("not special " + ts_code)
        
#maotai = pro.stock_basic(ts_code='600519.SH')




out_path = "C:\\Users\\terry\\Desktop\\110_Special_Price_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='6month_min')
output_df2.to_excel(writer, sheet_name='3month_min')
#output_df3.to_excel(writer, sheet_name='1month_min')
writer.save()
writer.close()








