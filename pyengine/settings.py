import os
from lib import utils

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.join(SRC_DIR, 'conf')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qh)8q53tg2v&zws-1pv_xl0o-*-zg76&3-pmw#)de-xhi&l^wo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.messages',
    #'django.contrib.staticfiles',
    'pyengine',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.security.SecurityMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'log_request_id.middleware.RequestIDMiddleware',
)

ROOT_URLCONF = 'pyengine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pyengine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pyengine',
        'USER': 'root',
        'HOST': 'localhost',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

PYENGINE = {
    'global': os.path.join(CONF_DIR, 'global.conf'),
    'router': os.path.join(CONF_DIR, 'router.conf'),
    'error': os.path.join(CONF_DIR, 'error.conf'),
    'plugin': os.path.join(CONF_DIR, 'plugin.conf'),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
		'request_id': {
			'()': 'log_request_id.filters.RequestIDFilter'
		}
    },
    'formatters': {
		'standard' : {
			'format':'%(asctime)s [%(levelname)s] %(request_id)s (%(filename)s:%(lineno)d) %(message)s',
			'datefmt' : '%b %d %H:%M:%S'
		}
    },
    'handlers': {
		'console':{
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'filters': ['request_id'],
			'formatter': 'standard'
		},
		'file':{
			'level' : 'DEBUG',
			'class' : 'logging.handlers.RotatingFileHandler',
			'filters': ['request_id'],
			'formatter': 'standard',
			'filename' : '/var/log/pyengine/api.log',
			'maxBytes': 10485760,
			'backupCount': 10
		}
    },
    'loggers': {
		'': {
			'handlers': ['console', 'file'],
			'propagate': False,
			'level': 'DEBUG'
		}
    }
}
