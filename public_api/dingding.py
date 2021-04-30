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
                buy_info = "报警：[买单成功]币种为:{},买单量为：{}, 详情：{}".format(market, quantity, res)
                self.dingding_warn(buy_info)
                return res
        except Exception as e:
            error_info = "报警：[买单失败]币种为:{},买单失败:{}".format(market, res)
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
                buy_info = "报警：[卖单成功]币种:{},卖单量为:{}".format(market, quantity)
                self.dingding_warn(buy_info)
                return res
        except BaseException as e:
            error_info = "报警：[卖单失败]币种为:{},卖单失败:{}".format(market, str(res))
            self.dingding_warn(error_info + str(res))
            return res

    def dingding_warn(self, text):
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        api_url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % dingding_token
        json_text = self._msg(text)
        try:
            requests.post(api_url, json.dumps(json_text), headers=headers, timeout=10)
        except Exception as e:
            print("钉钉发送异常:{}".format(str(e)))

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
