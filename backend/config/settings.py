import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str) -> str:
    return os.environ.get(name, default)


# --- Django core -------------------------------------------------------

SECRET_KEY = env("SESSION_SECRET", "changeme-session-secret")
DEBUG = env("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "quizbank",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / env("DATABASE_PATH", "./data/skilldrill.db"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth ------------------------------------------------------------------
# Django's own default (AUTH_PASSWORD_VALIDATORS = [] in global_settings.py)
# validates nothing -- the usual 4 validators only exist because the
# `startproject` template adds them, and this settings.py was hand-written.

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --- i18n ------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# --- CORS / sessions for the Vite frontend ---------------------------------

CORS_ALLOWED_ORIGINS = [env("CORS_ORIGIN", "http://localhost:5173")]
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [env("CORS_ORIGIN", "http://localhost:5173")]

# --- DRF ---------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
}

# --- SkillDrill app config (mirrors the old pydantic Settings) -------------

OLLAMA_HOST = env("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_GENERATION_MODEL = env("OLLAMA_GENERATION_MODEL", "qwen2.5:7b-instruct-q4_K_M")
OLLAMA_EMBEDDING_MODEL = env("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

GENERATION_BATCH_SIZE = int(env("GENERATION_BATCH_SIZE", "75"))
GENERATION_LOW_WATERMARK = int(env("GENERATION_LOW_WATERMARK", "15"))
GENERATION_MAX_RETRIES = int(env("GENERATION_MAX_RETRIES", "3"))
DEDUP_SIMILARITY_THRESHOLD = float(env("DEDUP_SIMILARITY_THRESHOLD", "0.9"))

SCENARIO_PASS_THRESHOLD = float(env("SCENARIO_PASS_THRESHOLD", "70"))
WEAK_TOPIC_THRESHOLD = float(env("WEAK_TOPIC_THRESHOLD", "70"))

TOP_UP_ENABLED = env("TOP_UP_ENABLED", "true").lower() == "true"
TOP_UP_INTERVAL_MINUTES = int(env("TOP_UP_INTERVAL_MINUTES", "30"))
TOP_UP_INITIAL_DELAY_SECONDS = int(env("TOP_UP_INITIAL_DELAY_SECONDS", "15"))
