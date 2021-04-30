# -*- coding: utf-8 -*-
import json
import os

from public_api.BinanceAPI import BinanceAPI
from public_api.authorization import api_key, api_secret

binan = BinanceAPI(api_key, api_secret)
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
        '''
        :param exchange: True 代表买入，取买入的仓位 False：代表卖出，取卖出应该的仓位
        :return:
        '''

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
        '''获取倍率系数'''
        data_json = self._get_json_data()
        return data_json['config']['RatioCoefficient']

    def get_profit_ratio(self):
        '''获取补仓比率'''
        data_json = self._get_json_data()
        return data_json['config']['profit_ratio']

    def get_double_throw_ratio(self):
        '''获取止盈比率'''
        data_json = self._get_json_data()
        return data_json['config']['double_throw_ratio']

    def set_ratio(self, symbol):
        '''修改补仓止盈比率'''
        data_json = self._get_json_data()
        ratio_24hr = binan.get_ticker_24hour(symbol)  #
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
