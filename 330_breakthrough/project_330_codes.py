import numpy as np
import pandas as pd
import baostock as bs
import datetime
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression

def stable_inc_price_judge(df):
    df2 = df[-21:-1]
    close_array = df2['close'].values #close_array = df2['close'].iloc[-31:-1].values
    time_series = np.arange(len(df2.index))
    df3 = df2.copy()
    df3["time_series"] = time_series
    x = df3.loc[:, ['time_series']]
    y = df3.loc[:, 'close'] # target
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    if slope > 0:
        if max(close_array)/min(close_array) <= 1.2:
            return True
        else:
            return False
        
def stable_flc_vol_judge(df):
    df2 = df[-21:-1]
    vol_array = df2['volume'].values
    if max(vol_array)/min(vol_array) <= 1.8:
        return True
    else:
        return False
        
    #vol_mean = vol_array.mean()
    #vol_rsd = vol_std/vol_mean

def breakthrough(df):
    if df['high'].values[-1] / df['close'].values[-1] > 1.01:
        if df['close'].values[-1] / df['open'].values[-1] >= 1.025 and df['volume'].values[-1] >= 1.5 * df['volume'].values[-2]:
            return True
        else:
            return False

def project_330(df, output_df):
    if breakthrough(df):
        if stable_inc_price_judge(df) and stable_flc_vol_judge(df):
            temp_df = pd.DataFrame({"stock":[code], "recent_close_price":[df['close'].values[-1]]})
            print("Congratulations! breakthrough "+code)
            output_df = pd.concat([output_df, temp_df])
    else:
        print("not breakthrough "+code)
    return output_df

lg = bs.login()
    

## get today date YYYYMMDD
#today_date = '2023-02-07'
today_date = pd.Timestamp('today').strftime("%Y-%m-%d")
today_datetime = datetime.datetime.strptime(today_date,'%Y-%m-%d')

months_ago_datetime = today_datetime + relativedelta(months=-2)  ## the datetime at x months ago
months_ago_date = pd.Timestamp(months_ago_datetime).strftime("%Y-%m-%d") #'2022-07-05'

## get all the stocks' data  
stock_rs = bs.query_all_stock(today_date)
stockdata = stock_rs.get_data()
stockdata = stockdata[~stockdata.code.str.startswith(('bj','sh.688','sh.0','sh.9','sz.1','sz.2','sz.39'))]


output_data_330 = {'stock': [], 'recent_close_price': []} 
output_df_330 = pd.DataFrame(output_data_330)
for code in stockdata['code']:     
    ###获取股票日K线数据###
    each_stock_data = bs.query_history_k_data(code, 
                                              "date,code,open,high,low,close,volume,tradeStatus",
                                              start_date=months_ago_date, end_date=today_date, 
                                              frequency="d", adjustflag="3")
    #### 打印结果集 ####
    result_list = []
    while (each_stock_data.error_code == '0') & each_stock_data.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(each_stock_data.get_row_data())
    df1 = pd.DataFrame(result_list, columns=each_stock_data.fields)
    #剔除停盘数据
    df1 = df1[df1['tradeStatus']=='1']
    df1.dropna()
    if len(df1.index) < 21: 
        continue
    df1['volume'].replace('', 0, inplace=True)
    df2 = df1.astype({'open':'float', 'high':'float','low':'float', 'close':'float', 'volume':'int64'})
    df2 = df2.round({'open': 2, 'high': 2, 'low': 2, 'close': 2})
    if df2['close'].values[-1] >= 100:
        continue
    df2 = df2.sort_values(by='date')
    output_df_330 = project_330(df2, output_df_330)

bs.logout()


#maotai = pro.stock_basic(ts_code='600519.SH')
out_path = "C:\\Users\\terry\\Desktop\\stock330_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df_330.to_excel(writer, sheet_name='330_20days')
writer.save()
writer.close()




