# posts/forms.py
from django import forms
from .models import Post

class BasePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["type","title","content","price_type","price","lat","lng","conditions"]
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("price_type") == Post.PriceType.PAID and cleaned.get("price") is None:
            self.add_error("price", "유료는 가격(원)이 필수입니다.")
        return cleaned

class DemandForm(BasePostForm):
    class Meta(BasePostForm.Meta):
        fields = BasePostForm.Meta.fields + ["usage","dry","package"]

class SupplyForm(BasePostForm):
    class Meta(BasePostForm.Meta):
        fields = BasePostForm.Meta.fields + ["amount"]
