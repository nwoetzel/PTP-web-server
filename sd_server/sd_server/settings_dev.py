# Django settings for sd_server project for development.
from settings_base import Base

class Dev(Base):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
