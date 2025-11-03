# cart/models.py
from django.conf import settings
from django.db import models

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = getattr(self.user, "nickname", None) or self.user.username
        return f"{name}님의 장바구니"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")  # ⬅️ 다시 non-null
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True, blank=True,   # ⬅️ 임시로 여기를 nullable
    )
    added_at = models.DateTimeField(auto_now_add=True)
    memo = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ("cart", "post")
        ordering = ["-added_at"]

    def __str__(self):
        # 임시 방어 (nullable 기간 중 에러 방지)
        cart_name = getattr(self.cart.user, "nickname", None) or getattr(self.cart.user, "username", "unknown")
        return f"[{cart_name}] {self.post or 'No-Post'}"
