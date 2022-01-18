import django_heroku

from .settings import *


django_heroku.settings(locals(), test_runner=False)
