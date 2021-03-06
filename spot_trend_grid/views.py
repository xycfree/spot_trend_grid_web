import json
import logging
import time
from django import views
from django.db.models import Q
from django.forms import model_to_dict

from data.calcIndex import CalcIndex
from public_api.BinanceAPI import BinanceAPI
from public_api.authorization import api_key, api_secret
from public_api.dingding import Message
from spot_trend_grid.batch_order import init_order
from spot_trend_grid.models import SpotConfigModel, NewsNoticeModel, BatchOrderDetailModel, BatchOrderModel

logger = logging.getLogger(__name__)

binan = BinanceAPI(api_key, api_secret)
msg = Message()

index = CalcIndex()

# 手续费
charge_amount = 0.00075


def get_symbol_account(symbol):
    """获取账户信息"""
    symbol = symbol.replace("USDT", "")
    try:
        res = binan.get_account()
        li = json.loads(res).get("balances", []) if isinstance(res, str) else res.get("balances", [])
        for i in li:
            if i["asset"] == symbol:
                free = float(i.get("free"))
                return free
    except Exception as e:
        logger.exception(f"Symbol:{symbol},获取账户可用数量异常:{e}")
        return 0


class SpotTrendGridView(views.View):

    def get_quantity(self, coin_info_obj, min_quantity=False, flag=True):
        """ 获取货币交易的买卖数量
        :param min_quantity: 用于控制减仓
        :param coin_info_obj: 当前仓位数据
        :param flag: True:表示买入，False:表示卖出，卖出时curr需要减一
        :return:
        """

        quantity_arr = coin_info_obj.quantity.split(",")  # 交易数量列表

        if min_quantity:
            quantity = quantity_arr[0]
        else:
            quantity_len = len(quantity_arr)  # 交易数量长度
            curr = coin_info_obj.current_num  # 当期下单次数
            if not flag:  # 卖出
                curr -= 1
                curr = curr if curr >= 0 else 0

            if curr < quantity_len:
                quantity = quantity_arr[curr]
            else:
                quantity = quantity_arr[-1]
        return float(quantity)

    def update_data(self, coin_info_obj, deal_price, step, current_num):
        """ 现货策略执行数据更新
        :param coin_info_obj: 交易对信息
        :param deal_price: 买价/卖价
        :param step: 步长
        :param current_num: 当前下单次数
        :return:
        """
        try:
            coin_info_obj.next_buy_price = round(deal_price * (1 - coin_info_obj.double_throw_ratio / 100),
                                                 coin_info_obj.min_num)
            coin_info_obj.grid_sell_price = round(deal_price * (1 + coin_info_obj.profit_ratio / 100),
                                                  coin_info_obj.min_num)
            coin_info_obj.step += step
            coin_info_obj.current_num += current_num
            coin_info_obj.current_num = max([0, coin_info_obj.current_num])
            coin_info_obj.free = get_symbol_account(coin_info_obj.coin_type)  # 货币可用数量
            coin_info_obj.save()
            logger.debug(f"交易对{coin_info_obj.coin_type},数据更新成功")
        except Exception as e:
            logger.exception(f"交易对{coin_info_obj.coin_type},数据更新异常:{str(e)}\n退出程序")
            exit()

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
                logger.debug(
                    f"{coin_info.coin_type}-当前价:{cur_market_price}--买入价:{grid_buy_price}--卖出价:{grid_sell_price}")

                # 设置的买入价 > 当前现货价格 and index.calcAngle->True
                if grid_buy_price >= cur_market_price and index.calcAngle(
                        coin_info.coin_type, "5m", False, right_size):  # 是否满足买入价

                    if current_num == max_count:
                        news, flag = NewsNoticeModel.objects.get_or_create(
                            coin_id=coin_info.id,
                            coin_type=coin_info.coin_type,
                            if_use=True,
                            defaults={"status": 1}
                        )
                        if flag:
                            logger.info(f"交易对:{coin_info.coin_type}--已买入最大次数[{current_num}]--暂停买入")
                            msg.dingding_warn(
                                "报警通知:\n" + "当前交易对:" + coin_info.coin_type + "连续买入次数已达" + str(current_num) + "次,暂停买入")
                            continue

                        elif flag is False and news.status == 0:  # 第一次或者status为0则发送
                            news.status = 1
                            news.save()
                            logger.info(f"交易对:{coin_info.coin_type}--已买入最大次数[{current_num}]--暂停买入")
                            msg.dingding_warn(
                                "报警通知:\n" + "当前交易对:" + coin_info.coin_type + "连续买入次数已达" + str(current_num) + "次,暂停买入")
                            continue
                        else:
                            logger.info(f"交易对:{coin_info.coin_type}--已买入最大次数[{current_num}]--暂停买入")
                            continue

                    # if float(current_num / max_count) > 0.8 and current_num != max_count:
                    #     quantity = self.get_quantity(coin_info, min_quantity=True)
                    #     logger.info(f"交易对:{coin_info.coin_type}-连续买入次数[{current_num}]-调整最低购买量[{quantity}]")
                    #     msg.dingding_warn("报警通知:\n" + "当前交易对:" + coin_info.coin_type + "连续买入次数已达" + str(
                    #         current_num) + "次,调整为最低购买量" + str(quantity))
                    # else:
                    # quantity = self.get_quantity(coin_info)  # 买入量

                    res = msg.buy_market_msg(coin_info.coin_type, quantity)  # 开市价单
                    if res['orderId']:  # 挂单成功
                        logger.info("买单挂单成功:{}".format(res))
                        self.update_data(coin_info, grid_buy_price, 1, 1)  # 修改买入卖出价格、当前步数,连续买入的次数

                        time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                    else:
                        logger.warning(f"买单挂单失败,失败原因:{res}")
                        time.sleep(60 * 5)

                elif grid_sell_price < cur_market_price and index.calcAngle(coin_info.coin_type, "5m", True,
                                                                            right_size):  # 是否满足卖出价
                    if step == 0:  # setp=0 防止踏空，跟随价格上涨
                        self.update_data(coin_info, grid_sell_price, step, 0)
                    else:
                        res = msg.sell_market_msg(coin_info.coin_type, self.get_quantity(coin_info, flag=False))
                        if res['orderId']:
                            logger.info("卖单挂单成功:{}".format(res))
                            money = float((1 - charge_amount)) * float(grid_sell_price) * quantity - float((
                                    1 + charge_amount)) * float(grid_buy_price) * quantity
                            income = coin_info.current_income

                            coin_info.current_income = money + float(income)

                            self.update_data(coin_info, grid_sell_price, -1, -1)

                            news1 = NewsNoticeModel.objects.filter(coin_id=coin_info.id)  # 修改钉钉通知状态
                            if news1 and news1[0].status == 1:
                                news1[0].status = 0
                                news1[0].save()

                            logger.info(
                                f"交易对:{coin_info.coin_type},卖出价[{grid_sell_price}],数量[{quantity}],赢利[{money}],总盈利[{coin_info.current_income}]")

                            msg.dingding_warn(
                                "卖单通知:\n" + "当前交易对:" + coin_info.coin_type + "卖出" + str(quantity) + "个,卖出价格是:" + str(
                                    grid_sell_price) + " USDT" + " 盈利:" + str(money) + "USDT" + "当前总盈利: " + str(
                                    coin_info.current_income) + "USDT")
                            time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                        else:
                            logger.warning(f"卖单挂单失败,失败原因:{res}")
                            time.sleep(60 * 5)
                else:
                    logger.debug("交易对:{},当前市价：{}。未能满足交易,继续运行".format(coin_info.coin_type, cur_market_price))
                time.sleep(5)
            except Exception as e:
                logger.exception(f"交易对:{coin_info.coin_type}运行失败,原因：{str(e)}")


class BatchOrderView(views.View):

    # def insert_order(self, order, info):
    def insert_order(self, info):
        try:
            if isinstance(info, list):
                # for t in info:
                    # order.batchorderdetailmodel_set.create(
                    #     **{"buy_price": t.get("buy_price"), "buy_amount": t.get("buy_amount")}).save()
                BatchOrderDetailModel.objects.bulk_create(
                    [BatchOrderDetailModel(buy_price=t.get("buy_price"),
                                           buy_amount=t.get("buy_amount"),
                                           buy_total_money=t.get("buy_total_money"),
                                           batch_order_id=t.get("batch_order_id"),
                                           sell_price=t.get("sell_price"),
                                           sell_amount=t.get("sell_amount"),
                                           sell_total_money=t.get("sell_total_money"),
                                           profit=t.get("profit")
                                           ) for t in info])

            else:
                # order.batchorderdetailmodel_set.create(
                #     **{"buy_price": info.get("buy_price"), "buy_amount": info.get("buy_amount")}).save()
                BatchOrderDetailModel.objects.create(
                    **{"buy_price": info.get("buy_price"), "buy_amount": info.get("buy_amount"),
                       "batch_order_id": info.get("batch_order_id")}).save()
            return True
        except Exception as e:
            logger.exception(f"分批建仓计划表插入异常:{e}")
            return False

    def update_order(self, order_id):
        try:
            order = BatchOrderModel.objects.get(id=order_id)
            order.status = 1
            order.save()
        except Exception as e:
            logger.exception(f"分批建仓策略表状态更新失败:{e}")

    def loop_run(self):
        orders = BatchOrderModel.objects.filter(if_use=True, status=0)
        # orders = [model_to_dict(order) for order in orders]
        logger.info(f"orders:{orders}")
        for order in orders:
            # fk = BatchOrderModel.objects.get(id=order.id)
            batch_order_id = order.id
            li = init_order(model_to_dict(order))
            for t in li:
                t['batch_order_id'] = batch_order_id

            logger.info(f"分批建仓计划表:{li}")

            res = self.insert_order(li)
            if res:
                self.update_order(batch_order_id)


class BatchOrderDetailView(views.View):
    def create_buy_order(self, info):
        # logger.info(f"create_buy_order_info:{info}")
        symbol = model_to_dict(BatchOrderModel.objects.get(id=info.get("batch_order_id"))).get("symbol")
        res = msg.buy_limit_msg(symbol, info.get("buy_amount"), info.get("buy_price"))
        if res.get("orderId"):  # 挂单成功
            logger.info("买单挂单成功:{}".format(res))
            self.update_order(res['orderId'], info, status=1)
        else:
            logger.exception(f"买单挂单异常:{res}")

    def create_sell_order(self, info):
        symbol = model_to_dict(BatchOrderModel.objects.get(id=info.get("batch_order_id"))).get("symbol")
        res = msg.sell_limit_msg(symbol, info.get("sell_amount"), info.get("sell_price"))
        if res.get("orderId"):  # 挂单成功
            logger.info("卖单挂单成功:{}".format(res))
            self.update_order(res['orderId'], info, status=3)
        else:
            logger.exception(f"卖单挂单异常:{res}")

    def check_order(self, info):
        logger.info("订单检查，并更新订单状态...")
        symbol = model_to_dict(BatchOrderModel.objects.get(id=info.get("batch_order_id"))).get("symbol")

        res = binan.get_order(symbol, info.get("order_id"))
        if res['orderId']:
            _status = res["status"]  # 订单状态 FILLED: 完全交易
            if _status == binan.order_status["filled"]:
                return True
                # status = 2 if info.get("status") == 1 else 4
                # self.update_order(info.get("order_id"), info, status)
        else:
            logger.exception(f"订单查询异常:{res}")
            return False

    def update_order(self, order_id, info, status):
        order_detail = BatchOrderDetailModel.objects.get(info.get("id"))
        order_detail.order_id = order_id
        order_detail.status = status
        order_detail.save()

    def loop_run(self):

        orders = BatchOrderModel.objects.filter(if_use=True, status=1)  # 已生成策略计划

        for order in orders:
            # logger.info(f"order:{model_to_dict(order)}")
            _order = model_to_dict(order)
            infos = BatchOrderDetailModel.objects.filter(Q(batch_order_id=_order.get("id")) & Q(status=0)).order_by("id")

            for info in infos:
                time.sleep(0.5)
                self.create_buy_order(model_to_dict(info))  # 挂买单

            info_buys = BatchOrderDetailModel.objects.filter(Q(batch_order_id=_order.get("id")) & Q(status=2)).order_by("id")
            for info in info_buys:
                self.create_sell_order(model_to_dict(info))  # 挂卖单

            buy_sell_info = BatchOrderDetailModel.objects.filter(Q(status=1) | Q(status=3)).order_by("id")
            for info in buy_sell_info:
                _info = model_to_dict(info)
                res = self.check_order(_info)
                if res:
                    # 订单更新
                    if info.status == 1:
                        info.status = 2
                    elif info.status == 3:
                        info.status = 4
                    info.save()
