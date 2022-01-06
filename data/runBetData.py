# -*- coding: utf-8 -*-
import json
import os
from decimal import Decimal

from data import binan
import logging
# from public_api.BinanceAPI import BinanceAPI
# from public_api.authorization import api_key, api_secret
#
# binan = BinanceAPI(api_key, api_secret)

logger = logging.getLogger(__name__)
# linux
data_path = os.getcwd() + "/data/data.json"


# windows
# data_path = os.getcwd() + "\data\data.json"

class RunBetData:

    def _get_json_data(self):
        '''读取json文件'''
        tmp_json = {}
        with open(data_path, 'r') as f:
            tmp_json = json.load(f)
            f.close()
        return tmp_json

    def _modify_json_data(self, data):
        '''修改json文件'''
        with open(data_path, "w") as f:
            f.write(json.dumps(data, indent=4))
        f.close()

    ####------下面为输出函数--------####

    def get_buy_price(self):
        data_json = self._get_json_data()
        return data_json["runBet"]["next_buy_price"]

    def get_sell_price(self):
        data_json = self._get_json_data()
        return data_json["runBet"]["grid_sell_price"]

    def get_cointype(self):
        data_json = self._get_json_data()
        return data_json["config"]["cointype"]

    def get_quantity(self, exchange_method=True):
        """
        :param exchange: True 代表买入，取买入的仓位 False：代表卖出，取卖出应该的仓位
        :return:
        """

        data_json = self._get_json_data()
        cur_step = data_json["runBet"]["step"] if exchange_method else data_json["runBet"]["step"] - 1  # 买入与卖出操作对应的仓位不同
        quantity_arr = data_json["config"]["quantity"]

        quantity = None
        if cur_step < len(quantity_arr):  # 当前仓位 > 设置的仓位 取最后一位
            quantity = quantity_arr[0] if cur_step == 0 else quantity_arr[cur_step]
        else:
            quantity = quantity_arr[-1]
        return quantity

    def get_step(self):
        data_json = self._get_json_data()
        return data_json["runBet"]["step"]

    def get_ratio_coefficient(self):
        """获取倍率系数"""
        data_json = self._get_json_data()
        return data_json['config']['RatioCoefficient']

    def get_profit_ratio(self):
        """获取补仓比率"""
        data_json = self._get_json_data()
        return data_json['config']['profit_ratio']

    def get_double_throw_ratio(self):
        """获取止盈比率"""
        data_json = self._get_json_data()
        return data_json['config']['double_throw_ratio']

    def get_atr(self, symbol, interval='4h', kline_num=20):
        """真实波动幅度均值（ATR）
            函数名：ATR
            名称：真实波动幅度均值
            简介：真实波动幅度均值（ATR)是 以 N 天的指数移动平均数平均後的交易波动幅度。 计算公式：一天的交易幅度只是单纯地 最大值 - 最小值。
            而真实波动幅度则包含昨天的收盘价，若其在今天的幅度之外：
            真实波动幅度 = max(最大值,昨日收盘价) − min(最小值,昨日收盘价) 真实波动幅度均值便是「真实波动幅度」的 N 日 指数移动平均数。
        """
        data = binan.get_klines(symbol, interval, kline_num)
        """
            [
            1499040000000,      // 开盘时间
            "0.01634790",       // 开盘价
            "0.80000000",       // 最高价
            "0.01575800",       // 最低价
            "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
            "148976.11427815",  // 成交量
            1499644799999,      // 收盘时间
            "2434.19055334",    // 成交额
            308,                // 成交笔数
            "1756.87402397",    // 主动买入成交量
            "28.46694368",      // 主动买入成交额
            "17928899.62484339" // 请忽略该参数
          ]
        """
        percent_total = 0
        for i in range(len(data)):
            percent_total = abs(float(data[i][3]) - float(data[i][2])) / float(data[i][4]) + percent_total
        atr_value = round(percent_total / kline_num * 100, 2)
        logger.debug(f"symbol: {symbol}, 真实波动幅度均值,atr_value: {atr_value}")
        return float(atr_value)

    def set_ratio(self, symbol):
        """修改补仓止盈比率"""
        data_json = self._get_json_data()
        ratio_24hr = binan.get_ticker_24hour(symbol)  #
        print(f"ratio_24hr: {ratio_24hr}")
        index = abs(ratio_24hr)

        if abs(ratio_24hr) > 6:  # 这是单边走势情况 只改变一方的比率
            if ratio_24hr > 0:  # 单边上涨，补仓比率不变
                data_json['config']['profit_ratio'] = 7 + self.get_step() / 4  #
                data_json['config']['double_throw_ratio'] = 5
            else:  # 单边下跌
                data_json['config']['double_throw_ratio'] = 7 + self.get_step() / 4
                data_json['config']['profit_ratio'] = 5

        else:  # 系数内震荡行情

            data_json['config']['double_throw_ratio'] = 5 + self.get_step() / 4
            data_json['config']['profit_ratio'] = 5 + self.get_step() / 4
        self._modify_json_data(data_json)

    # 买入后，修改 补仓价格 和 网格平仓价格以及步数
    def modify_price(self, deal_price, step):
        data_json = self._get_json_data()
        right_size = len(str(deal_price).split(".")[1])
        data_json["runBet"]["next_buy_price"] = round(
            deal_price * (1 - data_json["config"]["double_throw_ratio"] / 100), right_size)  # 保留2位小数
        data_json["runBet"]["grid_sell_price"] = round(deal_price * (1 + data_json["config"]["profit_ratio"] / 100),
                                                       right_size)
        data_json["runBet"]["step"] = step
        self._modify_json_data(data_json)
        print("修改后的补仓价格为:{double}。修改后的网格价格为:{grid}".format(double=data_json["runBet"]["next_buy_price"],
                                                           grid=data_json["runBet"]["grid_sell_price"]))


if __name__ == "__main__":
    instance = RunBetData()
    # print(instance.modify_price(8.87,instance.get_step()-1))
    print(instance.get_quantity(False))
    print(instance.get_atr("BTCUSDT"))
