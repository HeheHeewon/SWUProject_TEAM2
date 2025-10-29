# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=30, unique=True)  # 유지 가능
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    # ✅ createsuperuser가 nickname을 묻게 함
    REQUIRED_FIELDS = ["email", "nickname"]

    def __str__(self):
        return self.nickname or self.username
