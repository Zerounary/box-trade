#!/usr/local/bin/python3.7

import pandas as pd

stock_data = pd.read_csv("601881.d.20200101-20201222.csv", parse_dates=[1])

stock_data.sort_values('date', inplace=True)

# ma_list = [5, 20, 60]

# for ma in ma_list:
#   stock_data['MA_' + str(ma)] = stock_data['close'].rolling(ma).mean()

# for ma in ma_list:
#   stock_data['EMA_' + str(ma)] = pd.DataFrame.ewm(stock_data['close'], span=ma).mean()


stock_data['var2'] = var2 = stock_data['low'].shift(1);
stock_data['low_sub'] = low_sub = stock_data['low'].sub(var2)
stock_data['sam1'] = abs(low_sub)
stock_data['sam2'] = low_sub.apply(lambda x: max(x,0))
stock_data['SMA1'] = stock_data['sam1'].rolling(3).mean()
stock_data['SMA2'] = stock_data['sam2'].rolling(3).mean()
stock_data['var3'] = var3 = stock_data['SMA1'].div(stock_data['SMA2']).mul(100)
stock_data['var4'] = var4 = pd.DataFrame.ewm(var3 * 10, span=3).mean()
stock_data['var5'] = var5 = stock_data['low'].rolling(30).min()
stock_data['var6'] = var6 = var4.rolling(30).max()
stock_data['close_ma58'] = cma58 = stock_data['close'].rolling(58).mean()
stock_data['var7'] = var7 = stock_data['close_ma58'].apply(lambda x: 1 if x!=0 else 0 )
stock_data['arg8'] = arg8 = stock_data[['low','var4','var5','var6']].apply(lambda x: (x['var4'] + x['var6'] * 2)/2 if x['low'] <= x['var5'] else 0, axis=1)
stock_data['ema8'] = ema8 = pd.DataFrame.ewm(arg8, span=3).mean()
stock_data['var8'] = var8 = ema8.div(618).mul(var7)
stock_data['rst'] = stock_data['var8'].map(lambda x:("%.4f")%x)
stock_data.to_csv('zgyh_ma_ema.csv', index=False)
