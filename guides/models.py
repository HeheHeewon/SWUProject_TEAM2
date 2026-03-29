from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Guide(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guides")
    title = models.CharField(max_length=120)           # 예) '커피비누 만들기 DIY'
    summary = models.CharField(max_length=200, blank=True)

    thumbnail = models.ImageField(upload_to="guides/thumbs/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class GuideStep(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=80)            # 예) '재료준비', '혼합', '건조', ...
    # 아이콘은 간단히 이모지/문자(선택)로
    icon = models.CharField(max_length=10, blank=True) # 예) 🧪, 🧼, 🌿 등
    note = models.CharField(max_length=140, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"
