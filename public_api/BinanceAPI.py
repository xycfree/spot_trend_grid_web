# -*- coding: utf-8 -*
import hashlib
import hmac
import requests
import time

from public_api.authorization import recv_window, api_secret, api_key

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode


class BinanceAPI(object):
    test_flag = True
    if test_flag:
        print("开启测试环境")
        BASE_URL = "https://testnet.binance.vision/api/v1"
        BASE_URL_V3 = "https://testnet.binance.vision/api/v3"
        PUBLIC_URL = "https://www.binance.com/exchange/public/product"
    else:
        print("开启正式环境")
        BASE_URL = "https://www.binance.com/api/v1"
        BASE_URL_V3 = "https://api.binance.com/api/v3"
        PUBLIC_URL = "https://www.binance.com/exchange/public/product"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.order_status = {
            "new": "NEW",  # 订单被交易引擎接受
            "partially_filled": "PARTIALLY_FILLED",  # 部分订单被成交
            "filled": "FILLED",  # 订单完全成交
            "canceled": "CANCELED",  # 用户撤销了订单
            "pending_cancel": "PENDING_CANCEL",  # 撤销中(目前并未使用)
            "rejected": "REJECTED",  # 订单没有被交易引擎接受，也没被处理
            "expired": "EXPIRED",  # 订单被交易引擎取消, 比如LIMIT FOK 订单没有成交 市价单没有完全成交 强平期间被取消的订单 交易所维护期间被取消的订单
        }

    def ping(self):
        path = "%s/ping" % self.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    def get_ticker_price(self, market):
        path = "%s/ticker/price" % self.BASE_URL_V3
        params = {"symbol": market}
        res = self._get_no_sign(path, params)
        time.sleep(1)
        # print(f"get_ticker_price: {res}")
        return float(res['price'])

    def get_ticker_24hour(self, market):
        path = "%s/ticker/24hr" % self.BASE_URL_V3
        params = {"symbol": market}
        res = self._get_no_sign(path, params)
        return res

    # def get_ticker_24hour(self, market):
    #     path = "%s/ticker/24hr" % self.BASE_URL
    #     params = {"symbol": market}
    #     res = self._get_no_sign(path, params)
    #     return round(float(res['priceChangePercent']), 1)


    def get_klines(self, market, interval, limit=500, startTime=None, endTime=None):
        path = "%s/klines" % self.BASE_URL
        params = None
        if startTime is None:
            params = {"symbol": market, "interval": interval, "limit": limit}
        else:
            params = {"symbol": market, "limit": limit, "interval": interval, "startTime": startTime,
                      "endTime": endTime}
        return self._get_no_sign(path, params)

    def buy_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    def sell_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL", rate)
        return self._post(path, params)

    def buy_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY")
        return self._post(path, params)

    def sell_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL")
        return self._post(path, params)

    def get_order(self, symbol, order_id):
        """查询订单"""
        path = "%s/order" % self.BASE_URL_V3
        params = {"symbol": symbol, "orderId": order_id}
        return self._get(path, params)

    def get_positionInfo(self, symbol):
        """当前持仓交易对信息"""
        path = "%s/positionRisk" % self.BASE_URL
        params = {"symbol": symbol}
        time.sleep(1)
        return self._get(path, params)

    def get_account(self):
        """ 获取当前账户信息
    {
    "makerCommission": 10,
    "takerCommission": 10,
    "buyerCommission": 0,
    "sellerCommission": 0,
    "canTrade": true,
    "canWithdraw": true,
    "canDeposit": true,
    "updateTime": 1630433276401,
    "accountType": "SPOT",
    "balances": [
        {
            "asset": "BTC",
            "free": "0.00000000",
            "locked": "0.00000000"
        },
        {
            "asset": "BNB",
            "free": "0.00179363",
            "locked": "0.00000000"
        },
        {
            "asset": "QTUM",
            "free": "0.00000000",
            "locked": "0.00000000"
        },{
            "asset": "USDT",
            "free": "199.82661485",
            "locked": "0.00000000"
        }],
        "permissions": [
            "SPOT"
        ]
    }
        :return:
        """
        path = "%s/account" % self.BASE_URL_V3
        return self._get(path)


    ### ----私有函数---- ###
    def _order(self, market, quantity, side, price=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(price)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True).json()

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _post(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query, timeout=180, verify=True).json()

    def _get(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.get(url, headers=header, params=query, timeout=180, verify=True).json()




    def _format(self, price):
        return "{:.8f}".format(price)


if __name__ == "__main__":
    instance = BinanceAPI(api_key, api_secret)
    # print(instance.buy_limit("EOSUSDT",5,2))
    # print(instance.get_ticker_price("WINGUSDT"))
    # print(instance.get_ticker_24hour("WINGUSDT"))
    print(instance.get_account())