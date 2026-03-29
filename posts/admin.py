# posts/admin.py
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id", "type", "title", "author",
        "price_type", "price", "amount",
        "usage", "dry", "package", "within_5km",
        "demand_price_pref", "max_budget",
        "place_name", "created_at",
    )
    list_filter = (
        "type", "price_type", "usage", "dry", "package", "within_5km", "created_at",
    )
    search_fields = ("title", "content", "author__username", "author__nickname", "place_name", "address")
    ordering = ("-created_at",)
