#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-

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

box = Box('5.35', '16.94', '12.9')
# TODO 提供一个股票代码，自动计算当前的持仓位
stock = Stock(box, '30000')
warehouse = Warehouse('14.87', 3)
stockOpt = StockOperation(stock, warehouse, 5)
print(stockOpt)