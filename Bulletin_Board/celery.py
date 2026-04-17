import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bulletin_Board.settings')

app = Celery('Bulletin_Board')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'hourly_ads_newsletter': {
        'task': 'board.tasks.send_recent_ads_hourly',
        'schedule': 3600.0,
        'args': (1,),
    },
}
