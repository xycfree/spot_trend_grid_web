from django.contrib import admin

# Register your models here.
from .models import SpotConfigModel, NewsNoticeModel, BatchOrderModel, BatchOrderDetailModel


class SpotConfigModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'coin_type', "if_use", 'next_buy_price', 'grid_sell_price', 'step', 'profit_ratio', 'double_throw_ratio',
        'quantity', 'current_num', "max_count", "min_num", "current_income")

    fieldsets = (

        ("交易对", {'fields': (("coin_type", "if_use"))}),

        ('交易设置', {'fields': (
            ("next_buy_price", "grid_sell_price",), "step", "quantity", "current_num",
            ('profit_ratio', 'double_throw_ratio'))}),
        ("风控设置", {'fields': (("max_count", "min_num",))}),)

    search_fields = ("coin_type",)


class NewsNoticeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "coin_id", "coin_type", "status", "if_use")
    fields = ("id", "coin_id", "coin_type", "status", "if_use")


class BatchOrderModelAdmin(admin.ModelAdmin):

    list_display = (
        'id', "total_money", "order_interval", "order_interval_increase", "initial_invest_capital",
        "capital_interval_increase", "profit_ratio", "price_precision", "amount_precision",
        "buy_procedure_fee", "sell_procedure_fee", "if_use", "status"
    )

    fieldsets = (

        ("交易对", {'fields': (("symbol", "if_use"))}),

        ('交易设置', {'fields': ("total_money", "order_interval", "order_interval_increase", "initial_invest_capital",
                             "capital_interval_increase", "profit_ratio", "price_precision", "amount_precision",
                             "buy_procedure_fee", "sell_procedure_fee")}),
    )

    search_fields = ("symbol",)


class BatchOrderDetailModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', "buy_price", "buy_amount", "buy_total_money", "sell_price", "sell_amount", "sell_total_money",
        "total_money_usdt", "total_buy_symbol", "sell_profit_ratio", "profit", "current_average_price", "status",
         "batch_order_id"
    )

    def has_add_permission(self, request):
        """ 取消后台添加附件功能 """
        return False

    def has_delete_permission(self, request, obj=None):
        """ 取消后台删除附件功能 """
        return True

    def save_model(self, request, obj, form, change):
        """ 取消后台编辑附件功能 """
        return True


admin.site.register(SpotConfigModel, SpotConfigModelAdmin)
admin.site.register(NewsNoticeModel, NewsNoticeModelAdmin)
admin.site.register(BatchOrderModel, BatchOrderModelAdmin)
admin.site.register(BatchOrderDetailModel, BatchOrderDetailModelAdmin)
