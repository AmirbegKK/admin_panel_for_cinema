from config.settings import env

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'PORT': 5432,
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'options': '-c search_path=public,content',
        },
    },
}
