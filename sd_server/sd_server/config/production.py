# Django settings for sd_server project.
from .common import Common
from configurations import values

class Production(Common):
    SECRET_KEY = values.SecretValue()
