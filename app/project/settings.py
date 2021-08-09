"""
Django settings for project netflix_bot.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the netflix_bot like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET", "default")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", False)))

ALLOWED_HOSTS = ["it-garage.fun", "194.67.104.62"]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

if DEBUG:
    ALLOWED_HOSTS.append("*")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "netflix_bot.apps.ProjectConfig",
    "master.apps.MasterConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "../templates")],
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

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

KEY_PATH = os.getenv("KEY_PATH")
CERT_PATH = os.getenv("CERT_PATH")
BOT_PORT = os.getenv("BOT_PORT", 8443)
BOT_TOKEN = os.getenv("TOKEN")
MAIN_PHOTO = os.getenv("MAIN_PHOTO")

EMOJI = {"ok": "✅"}
ELEMENTS_PER_PAGE = 5

UPLOADER_ID = os.getenv("UPLOADER")
MOVIE_UPLOADER_ID = os.getenv("MOVIE_UPLOADER")

MASTER_TOKEN = os.getenv("MASTER_TOKEN")


def parse_list(value: str) -> list:
    return value.split(",")


MAIN_CHANNEL_ID = os.environ["MAIN_CHANNEL"]

# MAIN_CHANNEL_ID = UPLOADER_ID
CHAT_INVITE_LINK = os.environ["GET_INVITE_LINK"]

SITE_DOMAIN = os.environ.setdefault("DOMAIN", "127.0.0.1:88")  # "it_garage.fun"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

# Logging
LOG_INTO_FILE = os.environ.setdefault("LOG_INTO_FILE", "0") == "1"
LOG_FILE = os.environ.setdefault("LOG_FILE", "netflix.log")
UPLOAD_LOG_FILE = os.environ.setdefault("LOG_FILE", "upload.log")
LOG_LEVEL = os.environ.setdefault("LOG_LEVEL", "DEBUG")
LOG_FORMATTER_CONSOLE = os.environ.setdefault("LOG_FORMATTER_CONSOLE", "json")
LOG_FORMATTER_FILE = os.environ.setdefault("LOG_FORMATTER_FILE", "json")

handlers = ["stream"]
if LOG_INTO_FILE:  # pragma: no cover
    handlers.append("file")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] | %(funcName)+25s:%(lineno)+3s | %(levelname)+8s | %(message)s"
        },
        "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"},
    },
    "handlers": {
        "stream": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "json",
            "filename": LOG_FILE,
            "utc": True,
            "when": "midnight",
        },
        "upload_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "json",
            "filename": UPLOAD_LOG_FILE,
            "utc": True,
            "when": "midnight",
        },
    },
    "loggers": {
        "netflix_bot": {
            "handlers": handlers,
            "level": logging.INFO,
        },
        "bulkmail": {
            "handlers": ["stream"],
            "level": logging.INFO,
        },
        "master": {
            "handlers": handlers,
            "level": logging.INFO,
        },
        "error": {
            "handlers": ["stream"],
            "level": logging.INFO,
        },
        "uploader": {
            "handlers": ["upload_file", "stream"],
            "level": logging.INFO,
        },
    },
}
