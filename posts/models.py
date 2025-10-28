# posts/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class Post(models.Model):
    class Type(models.TextChoices):
        DEMAND = "DEMAND", "수요"
        SUPPLY = "SUPPLY", "공급"
    class Usage(models.TextChoices):
        COMPOST = "퇴비", "퇴비용"
        CRAFT   = "공예", "공예용"
    class Package(models.TextChoices):
        HAS  = "있음", "포장 있음"
        NONE = "없음", "포장 없음"
    class PriceType(models.TextChoices):
        FREE = "무료", "무료"
        PAID = "유료", "유료"

    type       = models.CharField(max_length=6, choices=Type.choices)
    title      = models.CharField(max_length=80)
    content    = models.TextField(blank=True)
    price_type = models.CharField(max_length=2, choices=PriceType.choices)
    price      = models.PositiveIntegerField(null=True, blank=True)
    lat        = models.FloatField()
    lng        = models.FloatField()
    conditions = models.CharField(max_length=120, blank=True)
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)

    # 수요 전용
    usage   = models.CharField(max_length=2, choices=Usage.choices, null=True, blank=True)
    dry     = models.BooleanField(null=True, blank=True)
    package = models.CharField(max_length=2, choices=Package.choices, null=True, blank=True)

    # 공급 전용
    amount  = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.price_type == self.PriceType.PAID and self.price is None:
            raise ValidationError({"price": "유료는 가격(원)이 필수입니다."})
        if self.type == self.Type.SUPPLY and not self.amount:
            raise ValidationError({"amount": "공급글은 수량/단위를 입력하세요."})

    def __str__(self): return f"[{self.get_type_display()}] {self.title}"

