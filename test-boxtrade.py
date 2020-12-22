#!/usr/local/bin/python3.7
# -*- encoding: utf-8 -*-
'''
@File    :   test-boxtrade.py
@Time    :   2020/12/22 21:17:43
@Author  :   Zerounary
@Version :   1.0
@Contact :   https://github.com/Zerounary
@Desc    :   None
'''

from BoxTrade import BoxStock, Warehouse, StockOperation

box_rade = BoxStock("sh.601881", fund='10000')
warehouse = Warehouse('12.14', 4)
stockOpt = StockOperation(box_rade.stock, warehouse, 1)
print(stockOpt)