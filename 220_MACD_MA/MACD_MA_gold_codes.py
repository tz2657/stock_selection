# import tushare as ts
# import numpy as np
import pandas as pd
import baostock as bs
import datetime
from dateutil.relativedelta import relativedelta
import talib as ta

def add_MACD(df):
    #获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
    #记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    #这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
    dif, dea, hist = ta.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    df["DIFF"], df["DEA"], df["MACD"] = dif, dea, hist
    return df

# def computeMACD(df):
#     #获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
#     #记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
#     #这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
#     dif, dea, hist = ta.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
#     macd_df = pd.DataFrame({'dif':dif[33:],'dea':dea[33:],'hist':hist[33:]},
#                            index=df['date'][33:],columns=['dif','dea','hist'])
#     # 删除空数据
#     # macd_df = macd_df.dropna()
#     return macd_df

def today_macd_judge(df):
    #判断MACD是否金叉
    #if ((macd_df.loc[-2,0] <= macd_df.iloc[-2,1]) & (macd_df.iloc[-1,0] >= macd_df.iloc[-1,1])):
    if ((df['DIFF'].values[-2] <= 1.05*df['DEA'].values[-2]) and (df['DIFF'].values[-1] >= 0.95*df['DEA'].values[-1])):
        return True
    else:
        return False

def add_MA(df): 
    ma_list = [5,10,20] ## 5,10,20 days mean average,etc days...
    for ma in ma_list:
        df['ma_' + str(ma)] = df['close'].rolling(ma).mean()
    return df

def today_ma_judge(df):
    ## 判断x日平均线是否金叉y日平均线
    if df['ma_5'].values[-1] >= df['ma_10'].values[-1] and df['ma_5'].values[-2] <= df['ma_10'].values[-2]:
        if df['ma_5'].values[-1] >= df['ma_20'].values[-1] and df['ma_5'].values[-2] <= df['ma_20'].values[-2]:
            if df['ma_10'].values[-1] >= df['ma_20'].values[-1] and df['ma_10'].values[-2] <= df['ma_20'].values[-2]:
                return True
    else:
        return False
    
def today_vol_judge(df):
    ##判断成交量是否是昨日的两倍以上
    if df['volume'].values[-1] >= 1.9 * (df['volume'].values[-2]):
        return True
    else:
        return False
    







lg = bs.login()

#today_date = '2023-02-03'
today_date = pd.Timestamp('today').strftime("%Y-%m-%d")
today_datetime = datetime.datetime.strptime(today_date,'%Y-%m-%d')
months_ago_datetime2 = today_datetime + relativedelta(days=-75) 
months_ago_date2 = pd.Timestamp(months_ago_datetime2).strftime("%Y-%m-%d") #'2022-07-05'
enddate = today_date
startdate = months_ago_date2
    
## get all the stocks' data  
stock_rs = bs.query_all_stock(today_date)
# #### 打印结果集 ####
# data_list = []
# while (stock_rs.error_code == '0') & stock_rs.next():
#     # 获取一条记录，将记录合并在一起
#     data_list.append(stock_rs.get_row_data())
# stockdata = pd.DataFrame(data_list, columns=stock_rs.fields)

stockdata = stock_rs.get_data()
stockdata = stockdata[~stockdata.code.str.startswith(('bj','sh.688','sh.0','sh.9','sz.1','sz.2','sz.39'))]


output_data = {'stock': [], 'recent_close_price': []} 
output_df = pd.DataFrame(output_data)
for code in stockdata['code']:
    # ts_code = row['ts_code']
    # df_each_stock = pro.daily(ts_code=ts_code,start_date='20230116',end_date='20230116').set_index('trade_date')
    # if len(df_each_stock.index) == 0:
    #     continue
    # df_each_stock = df_each_stock.sort_index()
    # macd_df1 = ts.util.formula.MACD(df_each_stock["close"][::-1], 3, 6, 3)
    # if macd_judge(macd_df1) and kdj_judge(kdj_df1):
    
    ###获取股票日K线数据###
    each_stock_data = bs.query_history_k_data(code,
                                 "date,code,high,low,close,volume,tradeStatus",
                                 start_date=startdate, end_date=enddate, 
                                 frequency="d", adjustflag="3")
    #### 打印结果集 ####
    result_list = []
    while (each_stock_data.error_code == '0') & each_stock_data.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(each_stock_data.get_row_data())
    df1 = pd.DataFrame(result_list, columns=each_stock_data.fields)
    df1.dropna()
    df1['volume'].replace('', 0, inplace=True)
    df1 = df1.astype({'high':'float','low':'float', 'close':'float', 'volume':'int64'})
    if len(df1.index) <= 34 or df1['close'].values[-1] >= 100:
        continue
    #剔除停盘数据
    df2 = df1[df1['tradeStatus']=='1']
    if len(df2.index) <= 34:
        continue
    df2 = df2.round({'high': 2, 'low': 2, 'close': 2})
    df2 = df2.sort_values(by='date')
    df3 = add_MA(df2)
    if today_ma_judge(df3):
        df3 = add_MACD(df3)
        if today_vol_judge(df3) and today_macd_judge(df3):
            temp_df = pd.DataFrame({"stock":[code], "recent_close_price":[df3['close'].values[-1]]})
            print("Congratulations! gold "+code)
            output_df = pd.concat([output_df, temp_df])
    else:
        print("not gold "+code)
        
bs.logout()


out_path = "C:\\Users\\terry\\Desktop\\220_MACD_MA_gold_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='MACD_MA_gold')
writer.save()
writer.close()

