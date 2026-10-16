
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "singano.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "role": "admin",
        "store": None,
    },
)

if created:
    user.set_password(password)
    user.save()
    print("Superuser created successfully.")
else:
    print("This username already exists. No changes were made.")
