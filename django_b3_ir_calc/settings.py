"""
Django settings for django_b3_ir_calc project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""



import os
from django.utils.translation import ugettext_lazy as _

IS_DOCKER = os.environ.get('IS_DOCKER', 0)
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if IS_DOCKER:
    SQLITE_DIR = BASE_DIR + '/sqlite'
else:
    SQLITE_DIR = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fgkx0r--c-5#k&vc5$1#!=6m2(5a(go5obgirw&g$!+b#9g^*)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'pdftotext',
    'file_upload',
    'stock_price',
    'b3_ir_calc',
    'report',
    'endorsement',
    'django_excel_csv',
    'reference_data',
    'charts',
    'corporate_events',
    'data_source',
    'django_b3_ir_calc',
    'trial',
    'social',

# The following apps are required by allauth:
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'alerts',
    'utils'
]

ACCOUNT_FORMS = {
    'login': 'allauth.account.forms.LoginForm',
    'signup': 'allauth.account.forms.SignupForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'set_password': 'allauth.account.forms.SetPasswordForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

]

ROOT_URLCONF = 'django_b3_ir_calc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': ['templates'],
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates', 'allauth')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

            'libraries':{
                'iterate_dicts': 'report.templatetags.iterate_dicts',
                }
        },
    },
]

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'django_b3_ir_calc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SQLITE_DIR, 'db.sqlite3'),
    }
}

#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_ROOT = os.path.join('/var/www/media/b3_ir_calc/')

MEDIA_URL = '/media/'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validationcsv.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/django_b3_ir_calc/static/"



STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


LANGUAGES = (
    ('en', _('English')),
    ('pt', _('Portuguese')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Para moeda Real Brasil
THOUSAND_SEPARATOR='.',
USE_THOUSAND_SEPARATOR=True


SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 3600000 # set just 10 seconds to test # Estah em 1000 horas, 40 dias.
SESSION_SAVE_EVERY_REQUEST = True # For anonymous user session


# Allauth
# ACCOUNT_AUTHENTICATION_METHOD='email'
# ACCOUNT_EMAIL_REQUIRED=True
# LOGIN_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_REDIRECT_URL = '/report/position'
ACCOUNT_LOGOUT_REDIRECT_URL ="/"



SITE_ID = 2


SERVER_EMAIL = 'sf@b3ircalc.online'
ADMINS = [('Koji', 'rbsnkjmr@gmail.com')]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django_b3_ir_calc/error.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

try:
    if IS_DOCKER:
        from django_b3_ir_calc.local_settings.local_settings import *
    else:
        from django_b3_ir_calc.local_settings import *
except ImportError as e:
    print("Failed to import local_settings.py")
