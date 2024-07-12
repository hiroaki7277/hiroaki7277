ALLOWED_HOSTS = ['162.43.85.85']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

python manage.py collectstatic


INSTALLED_APPS = [
    'DairinHP',  # 追加
]
