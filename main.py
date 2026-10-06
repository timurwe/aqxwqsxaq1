import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdz_project.settings')
django.setup()

app = get_asgi_application()