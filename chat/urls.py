# chat/urls.py
from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("start/<int:post_id>/", views.chat_start, name="start"),              # 거래하기 버튼
    path("room/<int:conversation_id>/", views.chat_room, name="room"),        # 채팅방
    path("inbox/", views.inbox, name="inbox"),
    # 채팅함

    # ✅ 제안 기능 (DEMAND 글 → 내 SUPPLY 글로 제안)
    path(
        "suggest/<int:demand_id>/",
        views.suggest_pick_supply,
        name="suggest_pick_supply",  # 🔥 여기 이름을 바꿔줘!
    ),
    path(
        "suggest/<int:demand_id>/<int:supply_id>/",
        views.suggest_with_supply,
        name="suggest_with_supply",
    ),

    path(
        "complete/<int:conversation_id>/",
        views.complete_trade,
        name="complete_trade",
    ),

    path("cancel/<int:conversation_id>/",
         views.cancel_trade,
         name="cancel_trade"),  # ← 추가# 거래 완료

    # ✅ JSON 메시지 API (폴링용)
    path(
        "room/<int:conversation_id>/messages-json/",
        views.messages_json,
        name="messages_json",
    ),
]
