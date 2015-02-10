'''
https://github.com/pydanny/cookiecutter-django
'''
from __future__ import absolute_import

from .develoment import Development
from .production import Production
try:
    from .server import Server
except:
    pass