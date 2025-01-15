from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_lms.settings')
app = Celery('final_lms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Beat schedule to run the task everyday
app.conf.beat_schedule = {
    'notify-overdue-users': {
        'task': 'book_flow.tasks.remind_users_overdue_books',   # Adjusted to match your app and task structure
        # 'schedule': crontab(minute="*")                         # Runs every 1 minute
        'schedule': crontab(hour=11, minute=00),                # Runs every day at 11:00 AM(+0Timezone)
        # 'schedule': crontab(minute="*/30")                    # Runs every 30 minute
    },
    'remind-due-users': {
        'task': 'book_flow.tasks.remind_users_due_books',
        'schedule': crontab(hour=11, minute=00),                # Runs every day at 11:00 AM(+0Timezone)
    },
}
