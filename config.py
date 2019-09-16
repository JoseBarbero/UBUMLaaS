from datetime import timedelta
# Create Celery beat schedule:
celery_get_manifest_schedule = {
    'schedule-name': {
        'task': 'ubumlaas.getManifest.periodic_run_get_manifest',
        'schedule': timedelta(seconds=300),
    },
}

class Config:
    CELERYBEAT_SCHEDULE = celery_get_manifest_schedule
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    REDIS_HOST = 'localhost'
    REDIS_PASSWORD = ''
    REDIS_PORT = 6379
    REDIS_URL = 'redis://localhost:6379/0'
