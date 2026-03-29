# chat/models.py
from django.conf import settings
from django.db import models
from posts.models import Post


class Conversation(models.Model):
    """
    하나의 글(Post)을 기준으로,
    buyer(구매자)와 seller(판매자) 사이에 1개의 채팅방.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="conversations")
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="buy_conversations",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sell_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🔥 새로 추가: 각 역할별 "마지막으로 읽은 시각"
    last_read_buyer = models.DateTimeField(null=True, blank=True)
    last_read_seller = models.DateTimeField(null=True, blank=True)


    class Meta:
        unique_together = ("post", "buyer", "seller")  # 같은 조합은 채팅방 1개만

    def __str__(self):
        return f"{self.post_id} / {self.buyer} -> {self.seller}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.conversation_id}] {self.sender}: {self.text[:20]}"


# ✅ 새로 추가: 거래 내역용 모델
class Trade(models.Model):
    """
    한 채팅방(Conversation)에 대해 1번만 생성되는 '거래 완료' 기록.
    - 판매자가 '구매 확정' 눌렀을 때 생성
    - 구매자 마이페이지에서 조회
    """
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="trade",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bought_trades",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sold_trades",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    memo = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.post.title} ({self.buyer} ↔ {self.seller})"
