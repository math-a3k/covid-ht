import os

from .settings import *

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 'DonTLoOkaTMeIMSeCrEt-rEsPeCt-OtHeRs-PrIvaCY!'
)

STATIC_ROOT = os.environ.get('STATIC_ROOT', '/vol/covid-ht/static/')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DATABASE_NAME', 'db.sqlite3'),
    }
}

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://{}:{}'.format(REDIS_HOST, REDIS_PORT),
    }
}
