# posts/forms.py
from django import forms
from .models import Post

# 희망 거래방식 선택지
CONDITION_CHOICES = [
    ("직거래", "직거래"),
    ("택배",   "택배"),
]

class BasePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title", "content",
        ]

# ── 수요글 폼 ───────────────────────────────────────────
class DemandForm(BasePostForm):
    """수요 전용: 용도/건조/포장/5km, 지불 의사(+예산), 희망 거래방식"""
    # 체크박스(다중선택)로 재정의
    conditions = forms.MultipleChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        label="희망 거래방식",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(BasePostForm.Meta):
        model = Post
        fields = BasePostForm.Meta.fields + [
            "usage", "dry", "package", "within_5km",
            "demand_price_pref", "max_budget",
            "conditions",  # ← 추가
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 수정화면: "직거래,택배" → ["직거래","택배"]
        if self.instance and self.instance.pk and self.instance.conditions:
            self.fields["conditions"].initial = [
                s for s in self.instance.conditions.split(",") if s
            ]

    def clean(self):
        cleaned = super().clean()
        # 수요글은 실제 금액을 저장하지 않음
        cleaned["price"] = None
        # 다중 선택을 "직거래,택배" 형태로 저장
        cond = cleaned.get("conditions")
        if isinstance(cond, (list, tuple)):
            cleaned["conditions"] = ",".join(cond)
        return cleaned

# ── 공급글 폼 ───────────────────────────────────────────
class SupplyForm(BasePostForm):
    """공급 전용: 가격유형(무료/유료) + 가격(유료시) + 수량/단위 + 희망 거래방식"""
    conditions = forms.MultipleChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        label="희망 거래방식",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta(BasePostForm.Meta):
        model = Post
        fields = BasePostForm.Meta.fields + [
            "place_name", "address",
            "conditions",
            "price_type", "price", "amount",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.conditions:
            self.fields["conditions"].initial = [
                s for s in self.instance.conditions.split(",") if s
            ]

    def clean(self):
        cleaned = super().clean()
        pt = cleaned.get("price_type")
        price = cleaned.get("price")
        if pt == Post.PriceType.PAID and price is None:
            self.add_error("price", "유료는 가격(원)이 필수입니다.")
        cond = cleaned.get("conditions")
        if isinstance(cond, (list, tuple)):
            cleaned["conditions"] = ",".join(cond)
        return cleaned
