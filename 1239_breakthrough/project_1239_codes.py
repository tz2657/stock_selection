import numpy as np
import pandas as pd
import baostock as bs
import datetime
from dateutil.relativedelta import relativedelta
import talib as ta
from sklearn.linear_model import LinearRegression

def add_MA(df, df_copy): 
    ma_list = [5] ## 5,10,20 days mean average,etc days...
    for ma in ma_list:
        df['ma_' + str(ma)] = df_copy['close'].rolling(ma).mean()
    return df


def add_MACD(df):
    # first 33 dif,dea,hist are Nan values
    dif, dea, hist = ta.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    df["DIFF"], df["DEA"], df["MACD"] = dif, dea, hist
    return df


def MACD_bt_div_judge(df):
    min_price_date = df.loc[df['close'].idxmin()]['date']
    #min_price_date_DIF = df[df['date'] == min_price_date]['DIFF'].values[0]
    #rec_min_DIF = df['DIFF'].min()
    min_DIF_date = df.loc[df['DIFF'].idxmin()]['date']
    if min_price_date > min_DIF_date: 
        return True
    else:
        return False


def stable_dec_vol_judge(df):
    df2 = df
    #vol_array = df2['volume'].values
    #vol_std = np.std(vol_array)
    time_series = np.arange(len(df2.index))
    df3 = df2.copy()
    df3["time_series"] = time_series
    x = df3.loc[:, ['time_series']]
    y = df3.loc[:, 'volume'] # target
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    if slope < 0:
        return True
    else:
        return False


def stable_dec_price_vol_judge(df):
    # pctchg_df = df['pctChg'].iloc[-30:]
    # pctchg_mean = pctchg_df.mean()
    # rsd_threshold = 1
    # rsd = pctchg_df.std()/abs(pctchg_mean)
    if len(df.index) <= 20:
        return False
    if df['close'].values[0] < df['close'].values[1]:
        return stable_dec_price_vol_judge(df[1:])
    df2 = df
    #close_array = df2['close'].values #close_array = df2['close'].iloc[-31:-1].values
    #close_std = np.std(close_array)
    #distance_array = np.diff(close_array)
    #distance_std = np.std(distance_array)
    time_series = np.arange(len(df2.index))
    df3 = df2.copy()
    df3["time_series"] = time_series
    x = df3.loc[:, ['time_series']]
    y = df3.loc[:, 'close'] # target
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    if slope < 0:
        y_pred = pd.Series(model.predict(x), index=x.index)
        errors = y-y_pred
        min_index = np.argmin(errors)
        max_index = min_index + np.argmax(errors[min_index:])
        if min_index in [0,1]:
            return stable_dec_price_vol_judge(df2[1:])
        elif df2['close'].values[max_index] > df2['close'].values[0]:
            return stable_dec_price_vol_judge(df2[max_index:])
        elif max_index >= len(df2.index) - 15:
            return False
        elif max_index - min_index >= 2:
            step1 = df3[:(min_index+1)]
            x1 = step1.loc[:, ['time_series']]
            y1 = step1.loc[:, 'close']
            model1 = LinearRegression()
            model1.fit(x1,y1)
            slope1 = model1.coef_[0]
          
            step3 = df3[max_index:]
            x3 = step3.loc[:, ['time_series']]
            y3 = step3.loc[:, 'close']
            model3 = LinearRegression()
            model3.fit(x3,y3)
            slope3 = model3.coef_[0]
            if (slope3 < 0) and (abs(slope1) > abs(slope3)):
                if stable_dec_vol_judge(df):
                    print("judge_start_date: " + df2['date'].values[0])
                    print("min_error_date: " + df2['date'].values[min_index])
                    print("max_error_date: " + df2['date'].values[max_index])
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False
        

def buy_breakthrough(df):
    recent_max_price = df['close'].values[-5:-1].max()
    #recent_min_vol = df['volume'].values[-5:-1].min()
    if df['volume'].values[-1] >= 2.5 * df['volume'].values[-2] and df['close'].values[-1] >= recent_max_price:
        return True
    else:
        return False


lg = bs.login()

#today_date = '2023-02-24'      
today_date = pd.Timestamp('today').strftime("%Y-%m-%d")
today_datetime = datetime.datetime.strptime(today_date,'%Y-%m-%d')
months_ago_datetime = today_datetime + relativedelta(months=-4)
months_ago_date = pd.Timestamp(months_ago_datetime).strftime("%Y-%m-%d") #'2022-07-05'
enddate = today_date
startdate = months_ago_date

## get all the stocks' data  
stock_rs = bs.query_all_stock(today_date)
stockdata = stock_rs.get_data()
stockdata = stockdata[~stockdata.code.str.startswith(('bj','sh.688','sh.0','sh.9','sz.1','sz.2','sz.39'))]

    
output_data = {'stock': [], 'recent_close_price': []} 
output_df = pd.DataFrame(output_data)
for code in stockdata['code']:
    each_stock_data = bs.query_history_k_data(code,
                                 "date,code,high,low,close,volume,pctChg,tradeStatus",
                                 start_date=startdate, end_date=enddate, 
                                 frequency="d", adjustflag="3")
    #### print the result ####
    result_list = []
    while (each_stock_data.error_code == '0') & each_stock_data.next():
        # append the result
        result_list.append(each_stock_data.get_row_data())
    df1 = pd.DataFrame(result_list, columns=each_stock_data.fields)
    df1.dropna()
    if len(df1.index) <= 70:
        continue
    df1['volume'].replace('', 0, inplace=True)
    df1 = df1.astype({'high':'float','low':'float', 'close':'float', 'volume':'int64'})
    if len(df1.index) <= 70 or df1['close'].values[-1] >= 100:
        continue
    # filter active tradeStatus
    df2 = df1[df1['tradeStatus']=='1']
    if len(df2.index) <= 70:
        continue
    df2 = df2.round({'high': 2, 'low': 2, 'close': 2})
    df2 = df2.sort_values(by='date')
    #df3 = add_MACD(df2)
    #if buy_breakthrough(df3) and MACD_bt_div_judge(df3):
    if df2['date'].values[-1] < today_date:
        continue
    df3 = df2[:-1]
    if buy_breakthrough(df2):
        if stable_dec_price_vol_judge(df3):
            temp_df = pd.DataFrame({"stock":[code], "recent_close_price":[df2['close'].values[-1]]})
            print("Congratulations! breakthrough12339 "+code)
            output_df = pd.concat([output_df, temp_df])
        #else:
            #print("not stable12339 "+code)
    #else:
        #print("not breakthrough12339 "+code)
        
bs.logout()


out_path = "C:\\Users\\terry\\Desktop\\12339_breakthrough_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='12339_breakthrough')
writer.save()
writer.close()


