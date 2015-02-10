# Django settings for sd_server project.
from .common import Common
from configurations import values

class Production(Common):
    SECRET_KEY = values.SecretValue()
    PBS_USER = ''
    PBS_PROXY_USER = ''
    
    @property
    def QSUB_FLAGS(self):
        flags = ""
        if not self.PBS_USER.empty():
            flags += " -u " + self.PBS_USER
        if not self.PBS_PROXY_USER.empty():
            flags += " -P " + self.PBS_PROXY_USER
        return flags
