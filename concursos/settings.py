"""
Django settings for concursos project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['VAR_SEC_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [os.environ['VAR_HOST_AWS'],os.environ['VAR_LOAD_BALANCER_PRIVADA'],os.environ['VAR_LOAD_BALANCER_PUBLICA']]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'WebConcursos',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'concursos.urls'

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

WSGI_APPLICATION = 'concursos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

###########################
# Configuración BD
###########################

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': os.environ['RDS_DB_NAME'],
#        'USER': os.environ['RDS_USERNAME'],
#        'PASSWORD': os.environ['RDS_PASSWORD'],
#        'HOST': os.environ['RDS_HOSTNAME'],
#        'PORT': os.environ['RDS_PORT'],
#    }
#}

# MongoDB

DATABASES = {
   'default': {
       'ENGINE': 'djongo',
       'NAME': os.environ['RDS_DB_NAME'],
       'HOST': os.environ['MONGO_HOST_NAME'],
#       'PORT': os.environ['MONGO_PORT'],
   }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es-CO'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/


#BOAA01
TEMPLATE_DIRS = [
    os.path.join('Proyecto_1.WebConcursos', 'templates'),
    os.path.join(BASE_DIR, 'templates'),
]

DATETIME_INPUT_FORMATS = '%Y-%m-%d'


#!!!!!!!!!!!!!!!!!!!!!!!!!!!
#STATIC_URL = '/static/media/'
#!!!!!!!!!!!!!
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#MEDIA_ROOT = os.environ['DIR_MEDIA_HOST'] - este no
############################
# Configuración EMAIL
############################

EMAIL_USE_TLS = 'True'
DEFAULT_FROM_EMAIL = 'supervoices.cloud@gmail.com'

EMAIL_BACKEND = os.environ['SES_EMAIL_BACKEND']
EMAIL_HOST = os.environ['SES_EMAIL_HOST']
EMAIL_PORT = os.environ['SES_EMAIL_PORT']
EMAIL_HOST_USER = os.environ['SES_EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['SES_EMAIL_HOST_PASSWORD']

#############################
# Adicion almacenamiento S3
#############################

#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, "assets"),
#    os.path.join(BASE_DIR, "media"),
#]

AWS_ACCESS_KEY_ID = os.environ['S3_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['S3_AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_AWS_STORAGE_BUCKET_NAME']
#AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# CloudFront

CLOUDFRONT_DOMAIN = os.environ['CFS3_CLOUDFRONT_DOMAIN'] #"your cloudfornt domain"
CLOUDFRONT_ID = os.environ['CFS3_CLOUDFRONT_ID']#"your cloud front id"
AWS_S3_CUSTOM_DOMAIN = os.environ['CFS3_CLOUDFRONT_DOMAIN']#"same as your cloud front domain" # to make sure the url that the files are served from this domain


#AWS_LOCATION = 'media'
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

#DEFAULT_FILE_STORAGE = 'concursos.storage_backends.MediaStorage'

###########

STATICFILES_STORAGE = 'concursos.storage_backends.StaticStorage'
DEFAULT_FILE_STORAGE = 'concursos.storage_backends.MediaStorage'

AWS_STATIC_LOCATION = 'static'
AWS_MEDIA_LOCATION = 'media'
AWS_PRC_MEDIA_LOCATION = '/media/procesados'

STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
MEDIA_ROOT = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_MEDIA_LOCATION)
#AWS_PROCESADOS_LOCATION = 'media/procesados'
#PRIVATE_FILE_STORAGE = 'concursos.storage_backends.ProcesadosStorage'


#DEFAULT_FILE_STORAGE = 'concursos.storage_backends.PublicMediaStorage'

# ElastiCache

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': [
            os.environ['CACHE_LOC_NAME']
        ],
        'OPTIONS': {
            'DB': 0,
            'MASTER_CACHE': os.environ['CACHE_LOC_NAME']
        },
    }
}
