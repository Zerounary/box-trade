#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import arrow
import decimal
from math import floor

decimal.getcontext().prec = 8
Decimal = decimal.Decimal


class Box:
  def __init__(self, bottom, top, priceLine):
    self.bottom = Decimal(bottom)
    self.top = Decimal(top)
    self.priceLine = Decimal(priceLine)

  @property
  def height(self):
    """
    价格区间
    """
    return self.top - self.bottom
  
  @property
  def priceTopDist(self):
    """
    顶距
    """
    return self.top - self.priceLine

  @property
  def priceBottomDist(self):
    """
    底距
    """
    return self.priceLine - self.bottom
  
  @property
  def priceTopRate(self):
    """
    顶距比
    """
    return self.priceTopDist / self.height
  
  @property
  def priceBottomRate(self):
    """
    底距比
    """
    return self.priceBottomDist / self.height

  def __str__(self):
    return 'Box(bottom={0.bottom}, top={0.top}, priceLine={0.priceLine}, height={0.height}, priceTopDist={0.priceTopDist}, priceBottomDist={0.priceBottomDist}, priceTopRate={0.priceTopRate}, priceBottomRate={0.priceBottomRate})'.format(self)

class Stock:
  def __init__(self, box, fund):
    self.box = box
    self.fund = Decimal(fund)

  @property
  def holdRate(self):
    """
    当前价位应该持仓的比例
    """
    return self.box.priceTopRate

  @property
  def holdAmount(self):
    """
    当前价位应该持仓的金额
    """
    return self.fund * self.holdRate

  @property
  def holdQuantity(self):
    """
    当前价位应该持仓的数量
    """
    return floor(self.holdAmount / self.box.priceLine / 100)

  def __str__(self):
    return 'Stock(box={0.box}, holdRate={0.holdRate}, holdAmount={0.holdAmount}, holdQuantity={0.holdQuantity})'.format(self)


class Warehouse:
  
  def __init__(self, costPrice, quantity):
    self.costPrice = Decimal(costPrice)
    self.quantity = Decimal(quantity)

  @property
  def costAmount(self):
    """
    成本金额
    """
    return self.costPrice * self.quantity * 100
  
  def __str__(self):
    return 'Warehouse(costPrice={0.costPrice}, quantity={0.quantity}, costAmount={0.costAmount})'.format(self)

class StockOperation:

  def __init__(self, stock, warehouse, unit):
    """
    :param stock: 当前的股票情况
    :param warehouse: 当前的仓位情况
    """
    self.stock = stock
    self.warehouse = warehouse
    self.unit = Decimal(unit)
  
  @property
  def quantityOperation(self):
    """
    操作数量：正数表示买入数量，负数表示卖出数量
    """
    return self.stock.holdQuantity - self.warehouse.quantity
  
  @property
  def AmountOperation(self):
    """
    操作金额：正数表示买入金额，负数表示卖出金额
    """
    return self.quantityOperation * 100 * self.stock.box.priceLine

  @property
  def gain(self):
    """
    操作盈亏：正数表示操作后盈利金额，负数表示操作后亏损金额
    """
    return self.AmountOperation - (self.warehouse.costPrice * self.quantityOperation * 100)
  
  @property
  def subPrice(self):
    """
    减手位：在这个价位，可以出单位手（unit）. 出手后的仓位比例
    """
    return self.stock.box.top - ((((self.warehouse.costAmount - (self.warehouse.costPrice * self.unit * 100))) / self.stock.fund) * self.stock.box.height)

  @property
  def addPrice(self):
    """
    减手位：在这个价位，可以出单位手（unit）. 出手后的仓位比例
    """
    return self.stock.box.top - ((((self.warehouse.costAmount + (self.warehouse.costPrice * self.unit * 100))) / self.stock.fund) * self.stock.box.height)

  def __str__(self):
    return 'StockOperation(warehouse={0.warehouse}, stock={0.stock}, quantityOperation={0.quantityOperation}, AmountOperation={0.AmountOperation}, unit={0.unit}, subPrice={0.subPrice}, addPrice={0.addPrice})'.format(self)


def rs2result(rs):
  data_list = []
  while (rs.error_code == '0') & rs.next():
      # 获取一条记录，将记录合并在一起
      data_list.append(rs.get_row_data())
  result = pd.DataFrame(data_list, columns=rs.fields)
  return result


def get_today_k_data(stock_code):
  lg = bs.login()
  # 显示登陆返回信息
  print('login respond error_code:'+lg.error_code)
  print('login respond  error_msg:'+lg.error_msg)
  start_date = arrow.now().shift(days=-20).format("YYYY-MM-DD")
  end_date = arrow.now().format("YYYY-MM-DD")
  rs = bs.query_history_k_data_plus(stock_code, "date,open,high,low,close,volume,amount", start_date=start_date, end_date=end_date, frequency="d", adjustflag="2")
  result = rs2result(rs)
  print(result)
  bs.logout()

  return result.tail(1)

def get_month_k_data(stock_code, start_date, end_date):
  csv_file_name = "m.{stock_code}-{start_date}-{end_date}.csv"
  result = None
  try:
    result = pd.read_csv(csv_file_name.format_map(vars()), parse_dates=[1])
  except Exception as e:
    print(e)
  
  if result is None:
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)
    rs = bs.query_history_k_data_plus(stock_code, "date,open,high,low,close,volume,amount", start_date=start_date, end_date=end_date, frequency="m", adjustflag="2")
    result = rs2result(rs)
    result.to_csv(csv_file_name.format_map(vars()), index=False)
    #### 登出系统 ####
    bs.logout()

  return result

class BoxStock:

  def __init__(self, stock_code, start_date = arrow.now().shift(years=-3).format("YYYY-MM-DD"), end_date=arrow.now().format("YYYY-MM-DD"), fund='20000'):
    self.box = self.getStockBox(stock_code, start_date, end_date)
    self.stock = Stock(self.box, fund)

  def getStockBox(self, stock_code, start_date, end_date):
    m_k_data = get_month_k_data(stock_code, start_date, end_date)
    d_k_date = get_today_k_data(stock_code)
    top = m_k_data['high'].max()
    #print('top:' + str(top))
    bottom = m_k_data['low'].min()
    price_line = d_k_date['close'].min()
    box = Box(bottom, top, price_line)
    return box

