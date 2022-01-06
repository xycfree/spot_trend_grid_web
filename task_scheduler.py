#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: 2021/9/9 19:55  @Author: xycfree  @Descript:

from apscheduler.schedulers.background import BackgroundScheduler


from tasks import SpotTrendGridViews,  BatchOrderDetailViews, BatchOrderViews
from spot_trend_grid_web import settings

scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
spot = SpotTrendGridViews()
scheduler.add_job(spot.spot_start_run, "interval", seconds=60, id="spot_grid_run", replace_existing=True)

# batch_order = BatchOrderViews()
# scheduler.add_job(batch_order.batch_order_start_run, "interval", seconds=120,
#                   id="batch_order_start_run", replace_existing=True)
#
# batch_order_detail = BatchOrderDetailViews()
# scheduler.add_job(batch_order_detail.batch_order_detail_start_run, "interval", seconds=120,
#                   id="batch_order_detail_start_run", replace_existing=True)


scheduler.start()


"""
删除任务

job = scheduler.add_job(myfunc, 'interval', minutes=2)
job.remove()

scheduler.add_job(myfunc, 'interval', minutes=2, id='my_job_id')
scheduler.remove_job('my_job_id')
"""