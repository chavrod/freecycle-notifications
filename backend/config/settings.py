"""
Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import json
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SITE_ID = 1
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load config
with open("/etc/pingcycle_config.json") as f:
    CONFIG = json.loads(f.read())

APP_NAME = CONFIG["APP_NAME"]


BASE_DOMAIN = CONFIG["BASE_DOMAIN"]


ENV = CONFIG["ENV"]
if ENV == "DEV":
    DEBUG = True

    WH_BASE_DOMAIN = CONFIG["DEV_WH_BASE_DOMAIN"]
    FRONTEND_ORIGIN = f"http://{BASE_DOMAIN}:3000"

    ALLOWED_HOSTS = ["*"]
    # CSRF
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_DOMAIN = BASE_DOMAIN
    CSRF_TRUSTED_ORIGINS = [FRONTEND_ORIGIN]
    # CORS
    CORS_ALLOW_ALL_ORIGINS = True

    SESSION_COOKIE_DOMAIN = BASE_DOMAIN
    SESSION_COOKIE_SECURE = False
else:
    DEBUG = False

    WH_BASE_DOMAIN = f"core.{BASE_DOMAIN}"
    FRONTEND_ORIGIN = f"https://{BASE_DOMAIN}"

    ALLOWED_HOSTS = [f".{BASE_DOMAIN}"]
    # CSRF
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_DOMAIN = f".{BASE_DOMAIN}"
    CSRF_TRUSTED_ORIGINS = [FRONTEND_ORIGIN]
    # CORS
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]
    # Session
    SESSION_COOKIE_SECURE = True

# Other CSRF
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False

# Other CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "x-email-verification-key",
    "x-csrftoken",
    "content-type",
    "x-password-reset-key",
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = CONFIG["DJANGO_SECRET_KEY"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "rest_framework",
    "anymail",
    # Authentication
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.usersessions",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # Local Apps
    "pingcycle.apps.users",
    "pingcycle.apps.core",
    # Scheduler
    "django_celery_beat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": CONFIG["DB_NAME"],
        "USER": CONFIG["DB_USER"],
        "PASSWORD": CONFIG["DB_PASSWORD"],
        "HOST": CONFIG["DB_HOST"],
        "PORT": CONFIG["DB_PORT"],
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Dublin"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Testing email
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    ANYMAIL = {
        "BREVO_API_KEY": CONFIG["BREVO_API_KEY"],
    }

DEFAULT_FROM_EMAIL = "PingCycle <no-reply@pingcycle.org>"


# Auth
AUTH_USER_MODEL = "users.CustomUser"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
ACCOUNT_ADAPTER = "pingcycle.apps.users.adapters.CustomAccountAdapter"
HEADLESS_ADAPTER = "pingcycle.apps.users.adapters.CustomHeadlessAdapter"

HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "account/verify-email/{key}",
    # Sent in an email when someone tries to signup with your email
    "account_reset_password": "account/password/reset",
    "account_reset_password_from_key": "account/password/reset/key/{key}",
    "account_signup": "account/signup",
}
# Use email for authentication instead of usernames.
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "\u200b"
TEMP_ALLOWED_EMAILS = CONFIG["TEMP_ALLOWED_EMAILS"]

##################
# Scraping Scheduler #
##################
TASKS_INTERVAL_MINUTES = 5
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = TASKS_INTERVAL_MINUTES * 60
CELERY_BROKER_URL = f"redis://{CONFIG['REDIS_HOST']}:6379/0"

##################
# Business Logic #
##################
MAX_KEYWORDS_PER_USER = CONFIG["MAX_KEYWORDS_PER_USER"]
MAX_CHATS_PER_USER = CONFIG["MAX_CHATS_PER_USER"]
if not isinstance(MAX_KEYWORDS_PER_USER, int):
    raise RuntimeError(
        f"'MAX_KEYWORDS_PER_USER' needs to be an integer, but got: {MAX_KEYWORDS_PER_USER}"
    )
CHAT_TEMP_UUID_MAX_VALID_SECONDS = 20
MAX_RETRIES_PER_MESSAGE = 3


if ENV != "DEV":
    sentry_sdk.init(
        dsn=CONFIG["SENTRY_DSN"],
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.01,
        send_default_pii=True,
    )
