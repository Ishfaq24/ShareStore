import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import cloudinary

# Load environment variables from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# Security / Debug
# ----------------------
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = 'RENDER' not in os.environ

# Render domain and optional external host
ALLOWED_HOSTS = ["*"]
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ----------------------
# Installed Apps
# ----------------------
INSTALLED_APPS = [
    "drive",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ----------------------
# Middleware
# ----------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serves static files efficiently
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ShareStore.urls"

# ----------------------
# Templates
# ----------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates/drive"],
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

WSGI_APPLICATION = "ShareStore.wsgi.application"

# ----------------------
# Database
# ----------------------

DATABASES = {
    "default" : dj_database_url.config(
        # Feel free to alter this value to suit your needs.
        default=os.getenv("CONNECTION_STRING"),
        conn_max_age=600
        )
     }

# ----------------------
# Authentication
# ----------------------
AUTH_USER_MODEL = "drive.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------
# Internationalization
# ----------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------
# Static files
# ----------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # optional if you have local static folders
if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ----------------------
# Media files (optional)
# ----------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------
# Cloudinary configuration
# ----------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# ----------------------
# Security headers (production)
# ----------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG and os.getenv("RENDER_EXTERNAL_HOSTNAME") is not None

