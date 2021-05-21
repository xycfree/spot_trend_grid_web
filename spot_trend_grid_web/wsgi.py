"""
WSGI config for spot_trend_grid_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spot_trend_grid_web.settings')

application = get_wsgi_application()


from apscheduler.schedulers.background import BackgroundScheduler


from tasks import SpotTrendGridViews
from spot_trend_grid_web import settings


scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
spot = SpotTrendGridViews()
scheduler.add_job(spot.spot_start_run, "interval", seconds=60, id="spot_grid_run", replace_existing=True)

scheduler.start()
