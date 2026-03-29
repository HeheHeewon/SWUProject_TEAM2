# cart/admin.py
from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__username", "user__nickname")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "post", "added_at")
    search_fields = ("cart__user__username", "post__title")
    autocomplete_fields = ("cart", "post")
