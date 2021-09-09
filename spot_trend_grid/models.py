from django.db import models


# Create your models here.


class SpotConfigModel(models.Model):
    id = models.AutoField(primary_key=True, help_text="自增id")
    next_buy_price = models.DecimalField(decimal_places=8, max_digits=16, help_text="下次开仓价(你下一仓位买入价)",
                                         verbose_name="下次开仓价")
    grid_sell_price = models.DecimalField(decimal_places=8, max_digits=16, help_text="当前止盈价(你的当前仓位卖出价)",
                                          verbose_name="当前止盈价")
    step = models.IntegerField(help_text="当前仓位(0:仓位为空)", verbose_name="当前仓位")
    profit_ratio = models.DecimalField(decimal_places=3, max_digits=4,
                                       help_text="止盈比率(卖出价调整比率。如：设置为5,即为5%，当前买入价为100，那么下次卖出价为105)", verbose_name="止盈比率")
    double_throw_ratio = models.DecimalField(decimal_places=3, max_digits=4,
                                             help_text="补仓比率(买入价调整比率。如：设置为5,即为5%当前买入价为100，那么下次买入价为95)",
                                             verbose_name="补仓比率")
    coin_type = models.CharField(max_length=16, help_text="交易对(你要进行交易的交易对，请参考币安现货。如：BTC 填入 BTCUSDT)",
                                 verbose_name="交易对")
    quantity = models.CharField(max_length=256, help_text="交易数量(第一手买入1,第二手买入2...超过第三手以后的仓位均按照最后一位数量(3)买入),例如:1,2,3",
                                verbose_name="交易数量")
    free = models.DecimalField(decimal_places=8, max_digits=10, help_text="可用货币数量", verbose_name="可用数量")
    max_count = models.IntegerField(help_text="连续买入而不卖出的最大次数", verbose_name="连续买入而不卖出的最大次数")
    min_num = models.IntegerField(help_text="交易金额最小位数长度,如0.00001,则填入5", verbose_name="交易金额最小位数长度")
    current_num = models.IntegerField(help_text="当前连续买入次数", verbose_name="当前连续买入次数", default=0)
    current_income = models.DecimalField(decimal_places=6, max_digits=10, help_text="当前收益", verbose_name="当前收益",
                                         default=0)
    if_use = models.BooleanField(verbose_name="是否启用", default=True)

    class Meta:
        verbose_name = '现货趋势策略'
        verbose_name_plural = '现货趋势策略'


class NewsNoticeModel(models.Model):
    id = models.AutoField(primary_key=True, help_text="自增id")
    coin_id = models.IntegerField(verbose_name="交易对ID", help_text="交易对ID,对应SpotConfigModel.id")
    coin_type = models.CharField(max_length=16, help_text="交易对,如BTC填入BTCUSDT)", verbose_name="交易对")
    status = models.IntegerField(verbose_name="钉钉通知标记", help_text="已达最大购买次数通知标记0:通知,1不通知")
    if_use = models.BooleanField(verbose_name="是否启用", default=True)

    class Meta:
        verbose_name = '最大购买次数通知标记'
        verbose_name_plural = '钉钉通知标记'


class BatchOrderModel(models.Model):

    id = models.AutoField(primary_key=True, help_text="自增id")
    symbol = models.CharField(verbose_name="交易对", max_length=32, help_text="交易对[BTCUSDT]")
    total_money = models.DecimalField(verbose_name="总投入资金", decimal_places=2, max_digits=10, default=1000)
    order_interval = models.FloatField(verbose_name="下单间距[%]", default=0.01)
    order_interval_increase = models.FloatField(verbose_name="下单递增间距[%]", default=0.3)
    initial_invest_capital = models.DecimalField(verbose_name="初始投入资金", default=20, decimal_places=2, max_digits=10)
    capital_interval_increase = models.FloatField(verbose_name="资金递增幅度[%]", default=0.25)
    profit_ratio = models.FloatField(verbose_name="利润比例[%]", default=0.05)
    price_precision = models.IntegerField(verbose_name="价格精度", default=2)
    amount_precision = models.IntegerField(verbose_name="数量精度", default=5)
    buy_procedure_fee = models.FloatField(verbose_name="买入手续费", default=0.001)
    sell_procedure_fee = models.FloatField(verbose_name="卖出手续费", default=0.001)
    if_use = models.BooleanField(verbose_name="是否启用", default=True)
    status = models.IntegerField(verbose_name="状态", default=0, help_text="0:未生成计划，1:已生成计划")

    class Meta:
        verbose_name = '现货分批策略'
        verbose_name_plural = '现货分批策略'


class BatchOrderDetailModel(models.Model):
    id = models.AutoField(primary_key=True, help_text="自增id")
    buy_price = models.DecimalField(verbose_name="买入单价", decimal_places=2, max_digits=10, default=0)
    buy_amount = models.DecimalField(verbose_name="买入数量", decimal_places=5, max_digits=10, default=0)
    buy_total_money = models.DecimalField(verbose_name="买入总价", decimal_places=2, max_digits=10, default=0)
    sell_price = models.DecimalField(verbose_name="卖出单价", decimal_places=2, max_digits=10, default=0)
    sell_amount = models.DecimalField(verbose_name="卖出数量", decimal_places=5, max_digits=10, default=0)
    sell_total_money = models.DecimalField(verbose_name="卖出总价", decimal_places=2, max_digits=10, default=0)
    total_money_usdt = models.DecimalField(verbose_name="累计金额USDT", decimal_places=2, max_digits=10, default=0)
    total_buy_symbol = models.DecimalField(verbose_name="累计买入量", decimal_places=5, max_digits=10, default=0)
    sell_profit_ratio = models.FloatField(verbose_name="卖出利润比例", default=0)
    profit = models.DecimalField(verbose_name="利润", decimal_places=2, max_digits=10, default=0)
    current_average_price = models.DecimalField(verbose_name="当前均价", decimal_places=2, max_digits=10, default=0)
    status = models.IntegerField(verbose_name="状态", default=0, help_text="1:买入挂单，2:已买入, 3:卖出挂单, 4:已卖出")
    # symbol_info = models.ForeignKey("BatchOrderModel", on_delete=models.CASCADE)
    batch_order_id = models.IntegerField(verbose_name="现货分批策略id")
    order_id = models.DecimalField(verbose_name="订单id", max_digits=16, decimal_places=0, default=0, null=True, blank=True)

    class Meta:
        verbose_name = '现货分批策略计划表'
        verbose_name_plural = '现货分批策略计划表'