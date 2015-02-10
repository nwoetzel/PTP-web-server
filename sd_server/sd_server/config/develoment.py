# Django settings for sd_server project for development.
from .common import Common

class Development(Common):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
