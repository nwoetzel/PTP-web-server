# Django settings for sd_server project.
from configurations import Configuration, values

import os

class Common(Configuration):
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # Local time zone for this installation. Choices can be found here:
    # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    # although not all choices may be available on all operating systems.
    # In a Windows environment this must be set to your system time zone.
    TIME_ZONE = values.Value('Europe/Berlin')
    
    # Language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE = values.Value('en-us')
    
    ADMINS = (
        # ('Your Name', 'your_email@example.com'),
    )
    
    MANAGERS = ADMINS
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.path.join(PROJECT_DIR,'sqlite.db'), # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': '',
            'PASSWORD': '',
            'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',                      # Set to empty string for default.
        }
    }
    
    # Hosts/domain names that are valid for this site; required if DEBUG is False
    # See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ['*']
    
    SITE_ID = values.IntegerValue(1)
    
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = values.BooleanValue(True)
    
    # If you set this to False, Django will not format dates, numbers and
    # calendars according to the current locale.
    USE_L10N = values.BooleanValue(True)
    
    # If you set this to False, Django will not use timezone-aware datetimes.
    USE_TZ = values.BooleanValue(True)
    
    # Absolute filesystem path to the directory that will hold user-uploaded files.
    # Example: "/var/www/example.com/media/"
    MEDIA_ROOT = values.PathValue( os.path.join(PROJECT_DIR,'upload',''))
    
    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash.
    # Examples: "http://example.com/media/", "http://media.example.com/"
    MEDIA_URL = values.Value('/download/')
    
    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/var/www/example.com/static/"
    STATIC_ROOT = values.PathValue( os.path.join(PROJECT_DIR,'static'))
    
    # URL prefix for static files.
    # Example: "http://example.com/static/", "http://static.example.com/"
    STATIC_URL = values.Value('/static/')
    
    # Additional locations of static files
    STATICFILES_DIRS = (
        # Put strings here, like "/home/html/static" or "C:/www/django/static".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        os.path.join(PROJECT_DIR,'resources'),
    )
    
    # List of finder classes that know how to find static files in
    # various locations.
    STATICFILES_FINDERS = values.BackendsValue([
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#        'django.contrib.staticfiles.finders.DefaultStorageFinder',
    ])
    
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
    # Note: This key only used for development and testing.
    #       In production, this is changed to a values.SecretValue() setting
    SECRET_KEY = 'CHANGEME!!!'
    
    # List of callables that know how to import templates from various sources.
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # Uncomment the next line for simple clickjacking protection:
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )
    
    ROOT_URLCONF = values.Value( 'sd_server.urls')
    
    # Python dotted path to the WSGI application used by Django's runserver.
    WSGI_APPLICATION = 'sd_server.wsgi.application'
    
    TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        os.path.join(PROJECT_DIR,'templates'),
    )
    
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # Uncomment the next line to enable the admin:
        'django.contrib.admin',
        # Uncomment the next line to enable admin documentation:
        # 'django.contrib.admindocs',
        'ptp',
        'gmyc',
    )
    
    # A sample logging configuration. The only tangible logging
    # performed by this configuration is to send an email to
    # the site admins on every HTTP 500 error when DEBUG=False.
    # See http://docs.djangoproject.com/en/dev/topics/logging for
    # more details on how to customize your logging configuration.
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'ptp': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'gmyc': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
        }
    }
    
    @property
    def QSUB_FLAGS(self):
        return []
    
    JOB_FOLDER = values.PathValue( MEDIA_ROOT)
    PYTHON_VIRTENV = ""
    PTP_PY         = values.PathValue( os.path.join( MEDIA_ROOT.default,"bin", "bPTP.py"))
    R_BINARY       = "R"
    GMYC_R         = values.PathValue( os.path.join( MEDIA_ROOT.default,"bin", "gmyc.script.R"))