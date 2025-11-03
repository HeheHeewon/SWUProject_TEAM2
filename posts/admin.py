# 테스트용

# posts/admin.py
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id","type","title","author","price_type","price","created_at")
    list_filter = ("type","price_type","usage","dry","package","created_at")
    search_fields = ("title","content","author__username","author__nickname")
    ordering = ("-created_at",)

