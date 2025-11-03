# posts/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Post(models.Model):
    class Type(models.TextChoices):
        DEMAND = "DEMAND", "수요"
        SUPPLY = "SUPPLY", "공급"

    class Usage(models.TextChoices):
        COMPOST  = "퇴비", "퇴비용"
        CRAFT    = "공예", "공예용"
        GARDEN   = "원예", "원예용"
        RESEARCH = "연구/실험", "연구/실험"
        ETC      = "기타", "기타"

    class Package(models.TextChoices):
        HAS  = "있음", "포장 있음"
        NONE = "없음", "포장 없음"

    class PriceType(models.TextChoices):
        FREE = "무료", "무료"
        PAID = "유료", "유료"
        # ANY = "상관", "상관없음"  # 필요시 해제

    # ── 공통 ──
    type       = models.CharField(max_length=6, choices=Type.choices)
    title      = models.CharField(max_length=80)
    content    = models.TextField(blank=True)

    # 공급 = 실제값 / 수요 = 선호값
    price_type = models.CharField(max_length=2, choices=PriceType.choices)
    price      = models.PositiveIntegerField(null=True, blank=True)

    # 위치
    lat        = models.FloatField(null=True, blank=True)
    lng        = models.FloatField(null=True, blank=True)
    place_name = models.CharField(max_length=80, blank=True)   # 거래장소명(예: 카페명)
    address    = models.CharField(max_length=255, blank=True)  # 도로명/지번

    conditions = models.CharField(max_length=120, blank=True)  # 거래/수거 조건 메모
    author     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ── 수요 전용 ──
    usage      = models.CharField(max_length=20, choices=Usage.choices, null=True, blank=True)
    dry        = models.BooleanField(null=True, blank=True)
    package    = models.CharField(max_length=2, choices=Package.choices, null=True, blank=True)
    within_5km = models.BooleanField(default=True)
    demand_price_pref = models.CharField(
        max_length=2,               # "무료"/"유료"
        choices=PriceType.choices,
        null=True, blank=True,
        help_text="무료/유료 중 선택",
    )
    max_budget = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="유료를 선택한 경우 최대 예산(원)",
    )

    # ── 공급 전용 ──
    amount = models.CharField(max_length=20, null=True, blank=True)  # 수량/단위

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["lat", "lng"]),
        ]

    def clean(self):
        # ── 공급글(SUPPLY) 유효성 ──
        if self.type == self.Type.SUPPLY:
            # 장소(이름 or 주소) 중 최소 1개 필수
            if not (self.place_name or self.address):
                raise ValidationError({
                    "place_name": "거래 장소명 또는 주소 중 하나는 입력하세요.",
                    "address": "거래 장소명 또는 주소 중 하나는 입력하세요.",
                })
            # 유료면 가격 필수
            if self.price_type == self.PriceType.PAID and self.price is None:
                raise ValidationError({"price": "유료는 가격(원)이 필수입니다."})
            # 수량/단위 필수
            if not self.amount:
                raise ValidationError({"amount": "공급글은 수량/단위를 입력하세요."})

        # ── 수요글(DEMAND) 유효성 ──
        if self.type == self.Type.DEMAND:
            # 수요글에는 실제 '거래가'를 입력하지 않음
            if self.price is not None:
                raise ValidationError({"price": "수요글에는 실제 금액을 입력하지 않습니다."})
            # 지불 의사 규칙
            if self.demand_price_pref == self.PriceType.PAID and self.max_budget is None:
                raise ValidationError({"max_budget": "유료를 원하면 최대 예산(원)을 적어주세요."})
            if self.demand_price_pref == self.PriceType.FREE and self.max_budget is not None:
                raise ValidationError({"max_budget": "무료만 원한다면 예산은 비워두세요."})

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"
