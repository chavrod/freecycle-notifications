import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable to the path of your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize the Django settings
django.setup()
