import json
import requests

from public_api.BinanceAPI import BinanceAPI
# windows
from public_api.authorization import dingding_token, api_secret, api_key


# linux
# from app.authorization import dingding_token

class Message:

    def buy_market_msg(self, market, quantity):
        try:
            res = BinanceAPI(api_key, api_secret).buy_market(market, quantity)
            if res['orderId']:
                buy_info = "报警：币种为：{cointype}。买单量为：{num}".format(cointype=market, num=quantity)
                print("买单成功:{}".format(buy_info))
                self.dingding_warn(buy_info)
                return res
        except BaseException as e:
            error_info = "报警：币种为：{cointype},买单失败:{err}.".format(cointype=market, err=str(res))
            print("买单失败:{}".format(error_info))
            self.dingding_warn(error_info)
            return res

    def sell_market_msg(self, market, quantity):
        '''
        :param market:
        :param quantity: 数量
        :param rate: 价格
        :return:
        '''
        try:
            res = BinanceAPI(api_key, api_secret).sell_market(market, quantity)
            if res['orderId']:
                buy_info = "报警：币种为：{cointype}。卖单量为：{num}".format(cointype=market, num=quantity)
                print("卖单成功:{}".format(buy_info))

                self.dingding_warn(buy_info)
                return res
        except BaseException as e:
            error_info = "报警：币种为：{cointype},卖单失败:{err}".format(cointype=market, err=str(res))
            print("卖单失败:{}".format(error_info))
            self.dingding_warn(error_info + str(res))
            return res

    def dingding_warn(self, text):
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % dingding_token
        json_text = self._msg(text)
        requests.post(api_url, json.dumps(json_text), headers=headers).content()

    def _msg(self, text):
        json_text = {
            "msgtype": "text",
            "at": {
                "atMobiles": [
                    "11111"
                ],
                "isAtAll": False
            },
            "text": {
                "content": text
            }
        }
        return json_text


if __name__ == "__main__":
    msg = Message()
