from django.db import models
from django.contrib.auth.models import User
# from [상품 앱 이름].models import Product  # 실제 프로젝트에서는 이렇게 상품 모델을 가져와야 합니다.

# 임시 상품 모델 (실제 구현 시 프로젝트의 Product 모델로 대체 필요)
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # ... 기타 상품 필드 ...

    def __str__(self):
        return self.name

# 장바구니 모델 (Cart)
# 장바구니는 사용자마다 하나씩 존재하며, 사용자와 1:1로 연결됩니다.
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}님의 장바구니'

# 장바구니에 담긴 상품 하나하나를 기록하는 모델 (Cart Item)
class CartItem(models.Model):
    # 이 아이템이 속한 장바구니 (Cart 삭제 시 아이템도 삭제)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    # 장바구니에 담긴 상품 (Product 삭제 시 아이템만 삭제, 장바구니는 유지)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # 상품의 수량
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} ({self.quantity}개)'

    # 상품 하나의 총 가격을 계산하는 속성
    @property
    def total_price(self):
        return self.product.price * self.quantity