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
            # "place_name", "address",
            # "conditions",
        ]


class DemandForm(BasePostForm):
    """수요 전용: 사용 용도/건조/포장/5km / 지불의사(무료·유료) + (유료시 최대예산)"""
    class Meta(BasePostForm.Meta):
        model = Post
        fields = BasePostForm.Meta.fields + [
            "usage", "dry", "package", "within_5km",
            "demand_price_pref", "max_budget",
        ]

    def clean(self):
        cleaned = super().clean()
        # 안전장치: 혹시 템플릿에서 price가 실수로 들어와도 폼 단계에서 제거
        cleaned["price"] = None
        return cleaned


class SupplyForm(BasePostForm):
    """공급 전용: 가격유형(무료·유료) + 가격(유료시) + 수량/단위"""

    # ✅ 복수 선택(체크박스). 드롭다운 다중 선택을 원하면 SelectMultiple로 교체 가능.
    conditions = forms.MultipleChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        label="희망 거래방식",
        widget=forms.CheckboxSelectMultiple
        # widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 2})
    )


    class Meta(BasePostForm.Meta):
        model = Post
        fields = BasePostForm.Meta.fields + [
            # 장소는 공급에서만 받음
            "place_name", "address",
            "conditions",
            "price_type", "price", "amount",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 수정 화면: "직거래,택배" → ["직거래","택배"] 로 초기화
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

        # ✅ 복수 선택값을 "직거래,택배" 형태의 문자열로 저장
        cond = cleaned.get("conditions")
        if isinstance(cond, (list, tuple)):
            cleaned["conditions"] = ",".join(cond)

        return cleaned