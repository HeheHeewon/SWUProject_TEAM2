from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),                 # 장바구니 목록
    path("add/<int:post_id>/", views.cart_add, name="cart_add"),     # 담기
    path("remove/<int:post_id>/", views.cart_remove, name="cart_remove"),  # 제거
]
