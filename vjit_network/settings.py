"""
Django settings for hutechsocial project.

Generated by 'django-admin startproject' using Django 2.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
from datetime import timedelta
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^pbni0gxx!lulz8evg17fb9c!w9h#_gu%nz(0%2aoe3_g-lkbv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SITE_ID = 1
# Application definition
INSTALLED_APPS = [
    'colorfield',
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'safedelete',
    'corsheaders',
    'drf_autodocs',
    'django_filters',
    'ckeditor',
    'debug_toolbar',
    'import_export',

    'vjit_network.core.apps.CoreConfig',
    'vjit_network.api.apps.ApiConfig',
    'vjit_network.common.apps.CommonConfig',
]

MIDDLEWARE = [
    'vjit_network.common.middlewares.RangesMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'vjit_network.common.middlewares.UserSettingMiddleware'
]

ROOT_URLCONF = 'vjit_network.urls'

AUTH_USER_MODEL = 'core.User'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR, ],
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

WSGI_APPLICATION = 'vjit_network.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vjit_network',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tb_cache',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = ('vjit_network.common.backends.CustomBackend',)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

LANGUAGES = [
    ('en', 'English'),
    ('vi',  'Tiếng Việt'),
    ('jp',  '日本語'),
]

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join('D://', 'mediafiles')

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'vjit_network.api.permissions.CustomDjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SEARCH_PARAM = 'search'

CKEDITOR_CONFIGS = {
    'default': {
        'type': 'inline',
        'width': '100%',
        'height': '5rem',
        'uiColor': '#92A8D1',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            # ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
            #     'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            # ['TextColor', 'BGColor'],
            # ['Styles', 'Format', 'Font', 'FontSize']
        ]
    }
}

# # logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s %(message)s')
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'D:\logging\hutechsns.log',
            'maxBytes': 1024 * 1024 * 1000,  # 1 GB,
            'backupCount': 3,
            'formatter': 'verbose',
            # 'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

# Email backend settings for Django
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'nguyenthanhdat.2741998@gmail.com'
EMAIL_HOST_PASSWORD = 'dat2741998'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://vjit.surge.sh',
    'https://vjit.surge.sh',
)

THUMBNAIL_DIMENTIONS = [(100, 100), (780, 780), (1024, 1024)]

INTERNAL_IPS = [
    '127.0.0.1',
]

# ONESIGNAL
ONESIGNAL_APP_ID = 'b5c7fd82-e7bd-48a2-9984-2232a1265969'
ONESIGNAL_REST_API_KEY = 'MGFlZWU3NTAtNzcxYS00OTIzLWJhYTYtY2IzMzQ5YTRmNWVk'
ONESINGAL_ANDROID_CHANNEL_ID = 'aae59f23-a9e4-4158-9c7a-59d6056235d2'

GRAPPELLI_INDEX_DASHBOARD = {
    'django.contrib.admin.site': 'vjit_network.core.admin.MyDashboard'}
GRAPPELLI_ADMIN_TITLE = 'VJIT Alumni'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# OTP
OTP_CODE_FROM = 1111
OTP_CODE_TO = 9999
OTP_EXPIRE_TYPE = 'minute'
OTP_EXPRIE_UNIT = 10

# phone format
PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'VN'