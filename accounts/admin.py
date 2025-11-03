from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

User = get_user_model()

class ProfileInline(admin.StackedInline):
    model = Profile           # Profile 모델에 user = OneToOneField(settings.AUTH_USER_MODEL, ...) 있어야 함
    fk_name = "user"          # Profile.user 필드명
    can_delete = False
    extra = 0
    verbose_name_plural = "profile"

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]  # Profile 없으면 이 줄 제거

    fieldsets = BaseUserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("nickname", "lat", "lng")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("nickname", "lat", "lng")}),
    )
    list_display = ("id", "username", "nickname", "email", "is_staff", "is_superuser")
    search_fields = ("username", "nickname", "email")
