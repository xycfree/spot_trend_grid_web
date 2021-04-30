# -*- coding: utf-8 -*-

from django import views

from spot_trend_grid.models import SpotConfigModel
from spot_trend_grid.views import SpotTrendGridView, logger


class SpotTrendGridViews(views.View):

    def spot_start_run(self):
        logger.info("定时任务开始执行")
        try:
            SpotTrendGridView().loop_run()
        except Exception as e:
            logger.error("定时任务异常," + str(e))
