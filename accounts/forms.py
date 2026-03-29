from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile # 이전에 작성한 Profile 모델 가져오기


User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nickname", "password1", "password2")

class ProfileForm(forms.ModelForm):
    # ModelForm을 상속받아 Profile 모델과 연결
    class Meta:
        model = Profile
        # 마이페이지에서 사용자가 수정할 수 있도록 허용할 필드 목록
        fields = ['phone_number', 'address'] 
        
        # 필드 표시 이름을 사용자 친화적으로 설정 (선택 사항)
        labels = {
            'phone_number': '전화번호',
            'address': '주소',
        }
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }