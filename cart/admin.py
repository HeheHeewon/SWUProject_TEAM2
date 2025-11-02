from django.contrib import admin
from .models import Product, Cart, CartItem

# 상품 모델 (임시) 등록
admin.site.register(Product) 

# 장바구니 아이템을 Cart 관리자 페이지에 함께 보여주기
class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ('product', 'quantity') # 관리자 실수 방지

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    inlines = (CartItemInline,)