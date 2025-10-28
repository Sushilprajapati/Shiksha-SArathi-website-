from pathlib import Path
import os
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 1. सुरक्षा और होस्टिंग सेटिंग्स (Production Ready) ---

# SECRET_KEY को एन्वायरनमेंट वेरिएबल से लें (सबसे सुरक्षित)
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-7lv5mf@px-1w*qkrc+5_kcja@j!f&nh6j20o@=b0^@#6eo!gqt' # लोकल उपयोग के लिए डिफ़ॉल्ट
)

# DEBUG सेटिंग को भी एन्वायरनमेंट वेरिएबल से लें।
DEBUG = os.environ.get('DEBUG') == 'True' 

# ALLOWED_HOSTS को एन्वायरनमेंट वेरिएबल से लें।
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = [
    'shiksha-sarathi-website.onrender.com', # आपका Render URL (सीधे भी रख सकते हैं)
    '127.0.0.1', 
    'localhost',
]

# Production के लिए ALLOWED_HOSTS को dynamic करें
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    # Render (या किसी भी प्रॉक्सी) के पीछे चलने पर HTTPS को सही से हैंडल करने के लिए
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Render URL को CSRF trusted origins में जोड़ें (लिंक समस्या के लिए सुरक्षा फिक्स)
    CSRF_TRUSTED_ORIGINS = ['https://' + RENDER_EXTERNAL_HOSTNAME]
    

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',  # आपका ऐप
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise को यहाँ जोड़ें (Static फ़ाइल की समस्या ठीक करने के लिए)
    # इसे SecurityMiddleware के ठीक बाद होना चाहिए
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'competition_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'competition_site.wsgi.application'


# --- 2. डायनामिक डेटाबेस कॉन्फ़िगरेशन (PostgreSQL/SQLite) ---

DATABASE_URL = os.environ.get('DATABASE_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production में PostgreSQL का उपयोग करें
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600  # कनेक्शन को सक्रिय रखता है
    )


# Password validation (No change needed)
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

# Internationalization (No change needed)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- 3. स्टैटिक फ़ाइल सेटिंग्स (WhiteNoise Fix) ---

# STATIC_URL: URL जहाँ से ब्राउज़र स्टैटिक फ़ाइलें लोड करेगा
STATIC_URL = '/static/'

# STATIC_ROOT: वह फ़ोल्डर जहाँ 'python manage.py collectstatic' सभी फ़ाइलों को कॉपी करेगा।
# Render इसी फ़ोल्डर को सर्व करता है।
STATIC_ROOT = BASE_DIR / 'staticfiles'

# STATICFILES_DIRS: वह फ़ोल्डर जहाँ Django लोकल में स्टैटिक फ़ाइलों को ढूँढता है।
STATICFILES_DIRS = [
    BASE_DIR / "static", 
]

# WhiteNoise का उपयोग करके Static फ़ाइलों को प्रबंधित करें (CSS/JS समस्या का समाधान)
# यह WhiteNoise को फ़ाइलों को कंप्रेस करने और परोसने के लिए कहता है।
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files (uploads like photos, PDFs)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 4. अन्य कॉन्फ़िगरेशन (जैसे ईमेल, पेमेंट) ---

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_RWCModYNZjsvEz') 
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'wX1JeMNbVY307k6MOakrmu2d')

# Email configuration 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# Port को integer में बदलें
try:
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
except ValueError:
    EMAIL_PORT = 587
    
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
