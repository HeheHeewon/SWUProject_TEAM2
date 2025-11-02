from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Profile 모델을 User 관리자 페이지에 함께 보여주기 위한 설정
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# 기존 UserAdmin을 확장하여 Profile을 추가
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# 기존 UserAdmin 등록 해제 후 새로운 UserAdmin 등록
admin.site.unregister(User)
admin.site.register(User, UserAdmin)