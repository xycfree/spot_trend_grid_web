import time
import logging
from django import views

from data.calcIndex import CalcIndex
from public_api.BinanceAPI import BinanceAPI
from public_api.authorization import api_key, api_secret
from spot_trend_grid.models import SpotConfigModel
from public_api.dingding import Message

logger = logging.getLogger(__name__)


binan = BinanceAPI(api_key, api_secret)
msg = Message()

index = CalcIndex()

# 手续费
charge_amount = 0.00075


class SpotTrendGridView(views.View):

    def get_quantity(self, coin_info_obj, min_quantity=False):
        '''
        :param exchange: min_quantity用于控制减仓
        :return:
        '''

        quantity_arr = coin_info_obj.quantity.split(",")

        if min_quantity:
            quantity = quantity_arr[0]
        else:
            quantity_len = len(quantity_arr)  # 交易量len
            curr = coin_info_obj.current_num  # 当期下单次数
            if curr < quantity_len:
                quantity = quantity_arr[curr]
            else:
                quantity = quantity_arr[-1]
        return float(quantity)

    def update_data(self, coin_info_obj, deal_price, step, current_num):
        """ 现货策略更新
        :param coin_info_obj: 交易对信息
        :param deal_price: 买价/卖家
        :param step: 步长
        :param current_num: 当前下单次数
        :return:
        """
        coin_info_obj.next_buy_price = round(deal_price * (1 - coin_info_obj.double_throw_ratio / 100),
                                             coin_info_obj.min_num)
        coin_info_obj.grid_sell_price = round(deal_price * (1 + coin_info_obj.profit_ratio / 100),
                                              coin_info_obj.min_num)
        coin_info_obj.step += step
        coin_info_obj.current_num += current_num
        coin_info_obj.current_num = max([0, coin_info_obj.current_num])
        coin_info_obj.save()

    def loop_run(self):
        for coin_info in SpotConfigModel.objects.filter(if_use=1):

            try:
                cur_market_price = binan.get_ticker_price(coin_info.coin_type)  # 当前交易对市价
                right_size = len(str(cur_market_price).split(".")[1])  # 小数点数位

                grid_buy_price = coin_info.next_buy_price  # 当前网格买入价格
                grid_sell_price = coin_info.grid_sell_price  # 当前网格卖出价格
                step = coin_info.step  # 当前步数
                current_num = coin_info.current_num  # 当前连续买入次数
                max_count = coin_info.max_count  # 连续买入而不卖出的最大次数
                quantity = self.get_quantity(coin_info)  # 买入量
                logger.info(f"{coin_info.coin_type}-当前价:{cur_market_price}--买入价:{grid_buy_price}--卖出价:{grid_sell_price}")

                # 设置的买入价 > 当前现货价格 and index.calcAngle->True
                if grid_buy_price >= cur_market_price and index.calcAngle(
                        coin_info.coin_type, "5m", False, right_size):  # 是否满足买入价

                    if float(current_num / max_count) > 0.6:
                        quantity = self.get_quantity(coin_info, min_quantity=True)
                        logger.info(f"交易对:{coin_info.coin_type}-连续买入次数[{current_num}]-调整最低购买量[{quantity}]")
                        msg.dingding_warn("报警通知:\n" + "当前交易对:" + coin_info.coin_type + "连续买入次数已达" + str(
                            current_num) + "次,调整为最低购买量" + str(quantity))
                    else:
                        quantity = self.get_quantity(coin_info)  # 买入量

                    if current_num == max_count:
                        logger.info(f"交易对:{coin_info.coin_type}--已买入最大次数[{current_num}]--暂停买入")
                        msg.dingding_warn(
                            "报警通知:\n" + "当前交易对:" + coin_info.coin_type + "连续买入次数已达" + str(current_num) + "次,暂停买入")
                        return

                    res = msg.buy_market_msg(coin_info.coin_type, quantity)
                    if res['orderId']:  # 挂单成功
                        logger.info("买单挂单成功:{}".format(res))
                        self.update_data(coin_info, grid_buy_price, 1, 1)  # 修改买入卖出价格、当前步数,连续买入的次数
                        time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                    else:
                        logger.warning(f"买单挂单失败,失败原因:{res}")
                        time.sleep(60*2)

                elif grid_sell_price < cur_market_price and index.calcAngle(coin_info.coin_type, "5m", True,
                                                                            right_size):  # 是否满足卖出价
                    if step == 0:  # setp=0 防止踏空，跟随价格上涨
                        self.update_data(coin_info, grid_sell_price, step, 0)
                    else:
                        res = msg.sell_market_msg(coin_info.coin_type, self.get_quantity(coin_info))
                        if res['orderId']:
                            logger.info("卖单挂单成功:{}".format(res))
                            money = float((1 - charge_amount)) * float(grid_sell_price) * quantity - float((
                                    1 + charge_amount)) * float(grid_buy_price) * quantity
                            income = coin_info.current_income

                            coin_info.current_income = money + float(income)

                            self.update_data(coin_info, grid_sell_price, -1, -1)
                            logger.info(f"交易对:{coin_info.coin_type},卖出价[{grid_sell_price}],数量[{quantity}],赢利[{money}],总盈利[{coin_info.current_income}]")

                            msg.dingding_warn(
                                "卖单通知:\n" + "当前交易对:" + coin_info.coin_type + "卖出" + str(quantity) + "个,卖出价格是:" + str(
                                    grid_sell_price) + " USDT" + " 盈利:" + str(money) + "USDT" + "当前总盈利: " + str(
                                    coin_info.current_income) + "USDT")
                            coin_info.save()

                            time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                        else:
                            logger.warning(f"卖单挂单失败,失败原因:{res}")
                            time.sleep(60 * 2)
                else:
                    logger.info("交易对:{coin_type},当前市价：{market_price}。未能满足交易,继续运行".format(
                        coin_type=coin_info.coin_type, market_price=cur_market_price))
                time.sleep(1)
            except Exception as e:
                logger.error(f"{coin_info.coin_type} 币种运行失败,原因为：{str(e)}")


