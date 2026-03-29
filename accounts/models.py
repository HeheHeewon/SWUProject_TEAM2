# accounts/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, OperationalError, ProgrammingError
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    nickname = models.CharField(max_length=30, unique=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    # createsuperuser 시 추가로 묻게 할 필드
    REQUIRED_FIELDS = ["email", "nickname"]   # 유지 가능

    def __str__(self):
        return self.nickname or self.username


class Profile(models.Model):
    # ✅ 항상 커스텀 사용자 모델을 참조하세요
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    total_transactions = models.IntegerField(default=0)

    def __str__(self):
        # 닉네임이 있으면 닉네임 표시
        u = getattr(self.user, "nickname", None) or self.user.username
        return f"{u} Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # 아직 테이블이 없을 때는 조용히 패스
            pass