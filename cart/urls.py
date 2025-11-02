from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # 장바구니 목록 보기
    path('', views.cart_detail, name='cart_detail'),
    
    # 장바구니에 상품 추가
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    
    # 장바구니에서 상품 제거
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
]