import os
from pathlib import Path

import dj_database_url
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-3!lk4on_*gy8um34369tlcf#)-fs9a9^nz!moq%=k)hy*9q=yj',
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

_allowed = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    'users',
    'products',
    'orders',
    'payments',
    'cms',
]

UNFOLD = {
    'SITE_TITLE': _('Oghie Store Admin'),
    'SITE_HEADER': _('Oghie Store'),
    'SITE_SUBHEADER': _('Super admin console'),
    'SITE_SYMBOL': 'storefront',
    'SITE_URL': '/',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': False,
    'SHOW_BACK_BUTTON': True,
    'BORDER_RADIUS': '6px',
    'COLORS': {
        'primary': {
            '50': '#ecfdf5',
            '100': '#d1fae5',
            '200': '#a7f3d0',
            '300': '#6ee7b7',
            '400': '#34d399',
            '500': '#10b981',
            '600': '#059669',
            '700': '#047857',
            '800': '#065f46',
            '900': '#064e3b',
            '950': '#022c22',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('Overview'),
                'separator': False,
                'items': [
                    {
                        'title': _('Dashboard'),
                        'icon': 'dashboard',
                        'link': reverse_lazy('admin:index'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Analytics API'),
                        'icon': 'monitoring',
                        'link': '/api/analytics/summary/',
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Commerce'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': _('Products'),
                        'icon': 'inventory_2',
                        'link': reverse_lazy('admin:products_product_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Categories'),
                        'icon': 'category',
                        'link': reverse_lazy('admin:products_category_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Currencies'),
                        'icon': 'payments',
                        'link': reverse_lazy('admin:products_currency_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Coupons'),
                        'icon': 'local_offer',
                        'link': reverse_lazy('admin:orders_coupon_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Fulfillment'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': _('Orders'),
                        'icon': 'receipt_long',
                        'link': reverse_lazy('admin:orders_order_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Carts'),
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:orders_cart_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Tracking Events'),
                        'icon': 'local_shipping',
                        'link': reverse_lazy('admin:orders_ordertrackingevent_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Payments'),
                        'icon': 'credit_card',
                        'link': reverse_lazy('admin:payments_payment_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Content'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': _('CMS Sections'),
                        'icon': 'web',
                        'link': reverse_lazy('admin:cms_cmssection_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Product Images'),
                        'icon': 'image',
                        'link': reverse_lazy('admin:products_productimage_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Reviews'),
                        'icon': 'reviews',
                        'link': reverse_lazy('admin:products_productreview_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Wishlists'),
                        'icon': 'favorite',
                        'link': reverse_lazy('admin:products_wishlistitem_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Access'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': _('Users'),
                        'icon': 'group',
                        'link': reverse_lazy('admin:auth_user_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Groups'),
                        'icon': 'admin_panel_settings',
                        'link': reverse_lazy('admin:auth_group_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': _('Profiles'),
                        'icon': 'badge',
                        'link': reverse_lazy('admin:users_userprofile_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'oghie.middleware.RequestLogMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oghie.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oghie.wsgi.application'

# Database — uses DATABASE_URL env var on Railway, falls back to SQLite locally
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files — WhiteNoise serves them in production
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files — Cloudinary in production, local disk in dev
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    import cloudinary

    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Additional security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CORS — allow frontend origin(s)
_cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'api.requests': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
