#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/7/8 10:02  @Author: xycfree  @Descript: 分批建仓
import json
import queue

from public_api.BinanceAPI import BinanceAPI
from public_api.authorization import api_secret, api_key

"""
投入总金额， 设置投资间距， 下一次递增幅度， 初始投资金额， 投资金额增幅， 利润比例， 价格精度， 数量精度， 买入手续费， 卖出手续费
"""

q = queue.Queue()
binance = BinanceAPI(api_key, api_secret)


def order_buy(*args, **kwargs):
    # 限价挂单买
    pass


def order_sess(*args, **kwargs):
    # 限价挂单卖
    pass


def get_price(symbol):
    return binance.get_ticker_price(symbol)


def init_order(data, *args, **kwargs):
    """ 初始化分批建仓策略
    :param data: 分批建仓策略数据
    :param args:
    :param kwargs:
    :return:
    """
    li = []
    init_flag = 0
    order_price = get_price(data.get("symbol"))  # 当前价
    print(f'symbol:{data.get("symbol")}, price:{order_price}')
    initial_invest_capital = float(data.get("initial_invest_capital"))  # 初始投资金额
    order_interval = float(data.get("order_interval"))  # 投资间隔
    order_interval_increase = float(data.get("order_interval_increase"))  # 投资间隔增幅
    capital_interval_increase = float(data.get("capital_interval_increase"))  # 投资间距增幅
    price_precision = data.get("price_precision")  # 价格精度
    amount_precision = data.get("amount_precision")  # 数量精度
    buy_procedure_fee = data.get("buy_procedure_fee")  # 买手续费
    sell_procedure_fee = data.get("sell_procedure_fee")  # 卖手续费
    profit_ratio = float(data.get("profit_ratio"))  # 利润
    total_money = float(data.get("total_money"))  # 总投资额
    _interval = 0

    while total_money > 0:

        if init_flag == 0:
            # 按当前价格下单，投资初始金额
            # _interval = _interval * order_interval_increase
            # order_price = round(order_price * (1 - _interval), price_precision)
            # init_flag += 1

            # 按投资间隔
            _interval = order_interval + _interval * order_interval_increase
            order_price = round(order_price * (1 - _interval), price_precision)
            init_flag += 1

        # elif init_flag == 1:
        #     _interval = order_interval + _interval * order_interval_increase
        #     order_price = round(order_price * (1 - _interval), price_precision)
        #     init_flag += 1
        else:
            _interval = _interval + _interval * order_interval_increase
            order_price = round(order_price * (1 - _interval), price_precision)
            init_flag += 1

        initial_invest_capital = initial_invest_capital * (
                1 + capital_interval_increase) if init_flag != 1 else initial_invest_capital

        initial_invest_capital = initial_invest_capital if total_money > initial_invest_capital else total_money
        amount = round(initial_invest_capital / order_price, amount_precision)

        sell_price = round(order_price * (1 + profit_ratio), price_precision)
        sell_amount = round(amount - (amount * buy_procedure_fee), amount_precision)
        buy_total_money = round(initial_invest_capital, price_precision)
        sell_total_money = round(sell_price * sell_amount, price_precision)
        di = {
            "symbol": data.get("symbol"),
            "buy_price": order_price,
            "buy_amount": amount,
            "buy_total_money": buy_total_money,
            "sell_price": sell_price,
            "sell_amount": sell_amount,
            "sell_total_money": sell_total_money,
            "profit": round(sell_total_money - buy_total_money, price_precision)

        }

        # di = {"symbol": data.get("symbol"), "buy_price": order_price, "invest_capital": initial_invest_capital,
        #       "profit_ratio": profit_ratio,  "amount": amount}

        li.append(di)
        total_money -= initial_invest_capital

    return li


def loop_run(data, *args, **kwargs):
    li = init_order(data)
    print(f"初始化分批建仓策略: {json.dumps(li, indent=2, ensure_ascii=False)}")

    for i in li:
        res = order_buy((i))
        if res:
            order_sess(i)


if __name__ == '__main__':
    """
    分批建仓策略
        total_money: 总投入资金
        order_interval: 下单间距
        order_interval_increase: 下单递增间距
        initial_invest_capital: 初始投入资金
        capital_interval_increase: 资金递增幅度
        profit_ratio: 利润比例
        price_precision: 价格精度
        amount_precision: 数量精度
        buy_procedure_fee: 买入手续费
        sell_procedure_fee: 卖出手续费
    """
    data = {
        "symbol": "ONEUSDT",
        "total_money": 100,  # 总投入资金
        "order_interval": 0.01,  # 下单间距%
        "order_interval_increase": 0.5,  # 下单递增间距%
        "initial_invest_capital": 11,  # 初始投入资金
        "capital_interval_increase": 0.25,  # 资金递增幅度%
        "profit_ratio": 0.066,  # 利润比例%
        "price_precision": 5,  # 价格精度
        "amount_precision": 5,  # 数量精度
        "buy_procedure_fee": 0.00075,  # 买入手续费
        "sell_procedure_fee": 0.00075,  # 卖出手续费
    }
    loop_run(data)
