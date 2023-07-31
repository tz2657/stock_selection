# import tushare as ts
# import numpy as np
import pandas as pd
import baostock as bs
import datetime
from dateutil.relativedelta import relativedelta
import talib as ta

# token = '7bc32e665d0c65878fd74a16f20ca6092e83c4b1ff1fd01c7c2ac3b3'
# api = ts.pro_api(token)
# pro = ts.pro_api(token)

# def df_add_macd(df) :
#     data = np.array(df.close)
#     ndata = len(data)
#     m, n, T = 12, 26, 9
#     EMA1 = np.copy(data)
#     EMA2 = np.copy(data)
#     f1 = (m-1)/(m+1)
#     f2 = (n-1)/(n+1)
#     f3 = (T-1)/(T+1)
#     for i in range(1, ndata):
#         EMA1[i] = EMA1[i-1]*f1 + EMA1[i]*(1-f1)
#         EMA2[i] = EMA2[i-1]*f2 + EMA2[i]*(1-f2)
#     df['ma1'] = EMA1
#     df['ma2'] = EMA2
#     DIF = EMA1 - EMA2
#     df['DIF'] = DIF
#     DEA = np.copy(DIF)
#     for i in range(1, ndata):
#         DEA[i] = DEA[i-1]*f3 + DEA[i]*(1-f3)
#     df['DEA'] = DEA
#     # ### tushare公式获取macd数据的方式
#     # macd = ts.util.formula.MACD(df["close"][::-1], 3, 6, 3)
#     # df['DIF'] = macd['DIFF']
#     # df['DEA'] = macd['DEA']
    
#     df['macd_金叉死叉'] = ''
#     macd_position = df['DIF'] > df['DEA']
#     df.loc[macd_position[(macd_position == True) & (macd_position.shift() == False)].index, 'macd_金叉死叉'] = '金叉'
#     df.loc[macd_position[(macd_position == False) & (macd_position.shift() == True )].index, 'macd_金叉死叉'] = '死叉'

# def df_add_kdj(df):
#     low_list=df['low'].rolling(window=9).min()
#     low_list.fillna(value=df['low'].expanding().min(), inplace=True)
#     high_list = df['high'].rolling(window=9).max()
#     high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    
#     rsv = (df['close'] - low_list) / (high_list - low_list) * 100
#     df['KDJ_K'] = rsv.ewm(com=2).mean()
#     df['KDJ_D'] = df['KDJ_K'].ewm(com=2).mean()
#     df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
#     df['KDJ_金叉死叉'] = ''
#     kdj_position = df['KDJ_K'] > df['KDJ_D']
#     df.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉'
#     df.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'


# # stockdata = pro.stock_basic(list_status='L', fields='ts_code')
# # stockdata = stockdata[~stockdata.ts_code.str.startswith(('688','8'))] ## filter out 688 stocks










def today_macd_judge(macd_df):
    #判断MACD是否金叉
    if ((macd_df.iloc[-2,0] <= macd_df.iloc[-2,1]) & (macd_df.iloc[-1,0] >= macd_df.iloc[-1,1])):
        return True
    else:
        return False
    #datenumber = int(macd_df.shape[0])
    #for i in range(datenumber-1):
        #if ((df3.iloc[i,0]<=df3.iloc[i,1]) & (df3.iloc[i+1,0]>=df3.iloc[i+1,1])):
    #macd_df.loc[macd_position[(macd_position == True) & (macd_position.shift() == False)].index, 'macd_金叉死叉'] = '金叉'
    #macd_df.loc[macd_position[(macd_position == False) & (macd_position.shift() == True )].index, 'macd_金叉死叉'] = '死叉'

def today_kdj_judge(kdj_df):
    if ((kdj_df.iloc[-2,0] <= kdj_df.iloc[-2,1]) & (kdj_df.iloc[-1,0] > kdj_df.iloc[-1,1])):
        return True
    else:
        return False
    # df_data['KDJ_金叉死叉'] = ''
    # kdj_position = df_data['K'] > df_data['D']
    # df_data.loc[kdj_position[(kdj_position == True) &
    #                          (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉'
    # df_data.loc[kdj_position[(kdj_position == False) &
    #                          (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'



def computeMACD(df):
    #获取dif,dea,hist，它们的数据类似是tuple，且跟df2的date日期一一对应
    #记住了dif,dea,hist前33个为Nan，所以推荐用于计算的数据量一般为你所求日期之间数据量的3倍
    #这里计算的hist就是dif-dea,而很多证券商计算的MACD=hist*2=(dif-dea)*2
    dif, dea, hist = ta.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    macd_df = pd.DataFrame({'dif':dif[33:],'dea':dea[33:],'hist':hist[33:]},
                           index=df['date'][33:],columns=['dif','dea','hist'])
    # 删除空数据
    # macd_df = macd_df.dropna()
    return macd_df



def computeKDJ(df):
    # low = df['low'].astype(float)
    # del df['low']
    # df.insert(0, 'low', low)
    # high = df['high'].astype(float)
    # del df['high']
    # df.insert(0, 'high', high)
    # close = df['close'].astype(float)
    # del df['close']
    # df.insert(0, 'close', close)
    # # 计算KDJ指标,前9个数据为空
    # low_list = df['low'].rolling(window=9).min()
    # high_list = df['high'].rolling(window=9).max()
    # rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    # df_kdj = pd.DataFrame()
    # df_kdj['K'] = rsv.ewm(com=2).mean()
    # df_kdj['D'] = df_data['K'].ewm(com=2).mean()
    # #df_kdj['J'] = 3 * df_data['K'] - 2 * df_data['D']
    # df_kdj.index = df['date'].values
    # df_kdj.index.name = 'date'
    # # 删除空数据
    # df_kdj = df_kdj.dropna()
    K, D = ta.STOCH(df['high'].values, 
                    df['low'].values, 
                    df['close'].values, 
                    fastk_period=9, 
                    slowk_period=3,
                    slowk_matype=0, 
                    slowd_period=3, 
                    slowd_matype=0)
    kdj_df = pd.DataFrame({'K':K,'D':D},
                           index=df['date'],columns=['K','D'])
    ####处理数据，计算J值
    kdj_df['K'].fillna(0,inplace=True)
    kdj_df['D'].fillna(0,inplace=True)
    #kdj_df['J']=3*df['K']-2*df['D']
    return(kdj_df)


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
stockdata = stockdata[~stockdata.code.str.startswith(('bj','sh.688','sh.0'))]


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
                                 "date,code,high,low,close,tradeStatus",
                                 start_date=startdate, end_date=enddate, 
                                 frequency="d", adjustflag="3")
    #### 打印结果集 ####
    result_list = []
    while (each_stock_data.error_code == '0') & each_stock_data.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(each_stock_data.get_row_data())
    df1 = pd.DataFrame(result_list, columns=each_stock_data.fields)
    if len(df1.index) <= 34:
        continue
    #剔除停盘数据
    df2 = df1[df1['tradeStatus']=='1']
    if len(df2.index) <= 34:
        continue
    df2.sort_values('date', inplace=True)
    df2 = df2.astype({'high':'float','low':'float', 'close':'float'})
    df2 = df2.round({'high': 2, 'low': 2, 'close': 2})
    try:
        macd_df = computeMACD(df2)
        kdj_df = computeKDJ(df2)
    except:
        print("error occured when computeMACD or computeKDJ"+code)
        continue
    if today_macd_judge(macd_df) and today_kdj_judge(kdj_df):
        temp_df = pd.DataFrame({"stock":[code], "recent_close_price":[df2['close'].values[-1]]})
        print("gold "+code)
        output_df = pd.concat([output_df, temp_df])
    else:
        print("not gold "+code)
        
        
bs.logout()
        




# df = pro.daily(ts_code='600519.SH', start_date='20220515', end_date='20220815').set_index('trade_date')
# df = df.sort_index()
#print(df)


out_path = "C:\\Users\\terry\\Desktop\\MACD_KDJ_gold_" + today_date + ".xlsx"
writer = pd.ExcelWriter(out_path , engine='xlsxwriter')
output_df.to_excel(writer, sheet_name='MACD_KDJ_gold')
writer.save()
writer.close()


