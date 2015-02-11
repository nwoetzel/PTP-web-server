'''
https://github.com/pydanny/cookiecutter-django
'''
from __future__ import absolute_import

# icnlude most specialized class first
from .server     import Server
from .production import Production
from .develoment import Development