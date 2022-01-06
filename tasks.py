# -*- coding: utf-8 -*-

from django import views

from spot_trend_grid.views import SpotTrendGridView, logger, BatchOrderDetailView, BatchOrderView


class SpotTrendGridViews(views.View):

    def spot_start_run(self):
        logger.debug("趋势策略定时任务开始执行")
        try:
            SpotTrendGridView().loop_run()
        except Exception as e:
            logger.exception("趋势策略定时任务异常," + str(e))


class BatchOrderViews(views.View):

    def batch_order_start_run(self):

        logger.debug("分批建仓定时任务开始执行")
        try:
            BatchOrderView().loop_run()
        except Exception as e:
            logger.exception("分批建仓定时任务异常," + str(e))


class BatchOrderDetailViews(views.View):

    def batch_order_detail_start_run(self):

        logger.debug("分批建仓计划表定时任务开始执行")
        try:
            BatchOrderDetailView().loop_run()
        except Exception as e:
            logger.exception("分批建仓计划表定时任务异常," + str(e))