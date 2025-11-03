# posts/forms.py
from django import forms
from .models import Post

class BasePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title", "content",
            # "place_name", "address",
            "conditions",
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
    class Meta(BasePostForm.Meta):
        model = Post
        fields = BasePostForm.Meta.fields + [
            # 장소는 공급에서만 받음
            "place_name", "address",
            "price_type", "price", "amount",
        ]


    def clean(self):
        cleaned = super().clean()
        pt = cleaned.get("price_type")
        price = cleaned.get("price")
        if pt == Post.PriceType.PAID and price is None:
            self.add_error("price", "유료는 가격(원)이 필수입니다.")
        return cleaned