# chat/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Q, Max, F, Case, When, BooleanField, Exists, OuterRef
)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from posts.models import Post
from .models import Conversation, Message, Trade


@login_required
def chat_start(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    seller = post.author
    buyer = request.user

    # 🔥 판매자가 자기 글에서 거래하기 눌렀을 때
    if buyer == seller:
        conv = Conversation.objects.filter(post=post).first()
        if conv:
            return redirect("chat:room", conversation_id=conv.id)

        messages.info(request, "아직 이 글에 대해 구매자가 채팅을 시작하지 않았습니다.")
        return redirect("chat:inbox")

    # 🔥 구매자가 ‘거래하기’ → 정상 채팅방 생성
    conv, created = Conversation.objects.get_or_create(
        post=post,
        buyer=buyer,
        seller=seller,
    )
    return redirect("chat:room", conversation_id=conv.id)


@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)

    # 🔒 참여자만 접근
    if request.user not in (conversation.buyer, conversation.seller):
        messages.error(request, "이 채팅방에 참여한 사용자만 접근할 수 있습니다.")
        return redirect("chat:inbox")

    post = conversation.post

    # 메시지 전송
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text,
            )
        return redirect("chat:room", conversation_id=conversation.id)

    # 🔥 GET 으로 방에 들어온 순간 → "여기까지 읽었다" 기록
    if request.method == "GET":
        now = timezone.now()
        if request.user == conversation.buyer:
            conversation.last_read_buyer = now
        elif request.user == conversation.seller:
            conversation.last_read_seller = now
        conversation.save(update_fields=["last_read_buyer", "last_read_seller"])

    messages_qs = conversation.messages.select_related("sender")

    return render(request, "chat/room.html", {
        "post": post,
        "conversation": conversation,
        "messages_qs": messages_qs,
    })


# ✅ DEMAND 글에서 “제안하기” 눌렀을 때: 내 SUPPLY 글들 고르는 화면
@login_required
def suggest_pick_supply(request, demand_id):
    """DEMAND 글에 제안할 때, 내가 가진 SUPPLY 글 목록을 보여주는 화면"""

    demand_post = get_object_or_404(Post, pk=demand_id, type=Post.Type.DEMAND)
    me = request.user
    demand_author = demand_post.author

    # 1️⃣ 이 수요글 기준으로 나(me)가 참여한 대화방이 있는지 확인
    conv = (
        Conversation.objects
        .filter(post=demand_post, buyer=me, seller=demand_author)
        .first()
    )

    # 2️⃣ 그 방에서 내가 한 번이라도 말한 적이 있으면 → 바로 채팅방으로
    if conv and conv.messages.filter(sender=me).exists():
        return redirect("chat:room", conversation_id=conv.id)

    # 내 공급글들
    my_supply_posts = Post.objects.filter(
        type=Post.Type.SUPPLY,
        author=request.user,
    )
    # my_supply_posts = my_supply_posts.filter(usage=demand_post.usage)  # 옵션

    return render(request, "chat/suggest_pick_supply.html", {
        "demand_post": demand_post,
        "my_supply_posts": my_supply_posts,
    })


# ✅ 선택한 SUPPLY 글로 실제 제안 보내기 (자동 메시지 + 중복/거래완료 체크)
@login_required
def suggest_with_supply(request, demand_id, supply_id):
    """
    DEMAND 글 + 선택한 SUPPLY 글을 묶어서 자동 메시지 전송.
      - 같은 수요글에 대해 여러 판매글 제안 가능 (같은 방에 쌓임)
      - 이미 제안했던 판매글이면 새 메시지 안 보내고 안내만 띄움
      - 이미 거래 완료된 판매글이면 제안 불가
    """
    demand_post = get_object_or_404(Post, pk=demand_id, type=Post.Type.DEMAND)
    supply_post = get_object_or_404(
        Post,
        pk=supply_id,
        type=Post.Type.SUPPLY,
        author=request.user,          # 내 글만 허용
    )

    me = request.user                 # 제안자
    demand_author = demand_post.author  # 수요글 글쓴이

    # 🔥 공급글이 이미 '거래 완료'라면 제안 차단
    is_already_traded = Trade.objects.filter(post=supply_post).exists()
    if is_already_traded:
        messages.warning(request, "이미 거래 완료된 판매글이라 제안할 수 없습니다.")
        return redirect("chat:suggest_pick_supply", demand_id=demand_id)

    # DEMAND 글 기준으로 대화방 생성/조회
    conv, created = Conversation.objects.get_or_create(
        post=demand_post,
        buyer=me,
        seller=demand_author,
    )

    # 이 판매글 상세 URL (절대경로)
    supply_url = request.build_absolute_uri(
        reverse("posts:detail", args=[supply_post.pk])
    )

    # 🔥 이미 이 판매글을 한 번이라도 제안했는지
    already_suggested_this = conv.messages.filter(
        sender=me,
        text__contains=supply_url,   # URL 기준으로 동일 판매글 제안 체크
    ).exists()

    if already_suggested_this:
        messages.info(request, "이미 이 판매글로 제안을 보냈습니다.")
        return redirect("chat:room", conversation_id=conv.id)

    # 🔥 여기서 내가 이 채팅방에서 한 번이라도 말한 적이 있는지 확인
    has_my_message = conv.messages.filter(sender=me).exists()

    if not has_my_message:
        # 첫 제안
        prefix = (
            f"안녕하세요, '{demand_post.title}' 글 보고 연락드렸어요.\n"
            f"제가 올린 판매글: {supply_post.title}\n"
        )
    else:
        # 두 번째 이후, '다른' 판매글 제안
        prefix = f"추가로 제안드려요: {supply_post.title}\n"

    button_html = (
        f'<a href="{supply_url}" '
        f'class="btn btn-sm btn-secondary" target="_blank">'
        f'판매글 보러가기'
        f'</a>'
    )

    text = prefix.replace("\n", "<br>") + "<br>" + button_html

    Message.objects.create(
        conversation=conv,
        sender=me,
        text=text,
    )

    return redirect("chat:room", conversation_id=conv.id)


@login_required
def inbox(request):
    """
    채팅함
      - role=seller     : 내가 '판매자'로 참여한 채팅 (SUPPLY 글의 글쓴이,
                           + 구매자가 실제로 메시지를 보낸 경우만)
      - role=buyer      : 내가 '구매자'로 참여한 채팅 (SUPPLY 글에 문의/거래,
                           + 내가 실제로 메시지를 보낸 경우만)
      - role=proposer   : 내가 '제안자'로 참여한 채팅 (DEMAND 글에 제안 보냄,
                           + 내가 실제로 메시지를 보낸 경우만)
      - role=receiver   : 내가 '제안을 받은 수요자'인 채팅 (내 DEMAND 글에 온 제안,
                           + 제안자가 실제로 메시지를 보낸 경우만)
      - role=all / 없음 : 내가 참여한 모든 채팅
    """
    role = request.GET.get("role", "all")

    # 0) 기본: 내가 참여한 모든 대화
    qs = (
        Conversation.objects
        .filter(Q(buyer=request.user) | Q(seller=request.user))
        .select_related("post", "buyer", "seller")
    )

    # 1) 먼저 "최근 메시지 시각, 안 읽은 메시지 여부"를 annotate
    qs = qs.annotate(
        last_message_at=Max("messages__created_at"),
        has_unread=Case(
            # 내가 buyer 인데, seller 가 보낸 메시지 중
            # last_read_buyer 이후(또는 아직 한 번도 안 읽음)가 존재하면 True
            When(
                Q(buyer=request.user)
                & Q(messages__sender=F("seller"))
                & (
                    Q(last_read_buyer__isnull=True)
                    | Q(messages__created_at__gt=F("last_read_buyer"))
                ),
                then=True,
            ),
            # 내가 seller 인데, buyer 가 보낸 메시지 중
            # last_read_seller 이후(또는 아직 한 번도 안 읽음)가 존재하면 True
            When(
                Q(seller=request.user)
                & Q(messages__sender=F("buyer"))
                & (
                    Q(last_read_seller__isnull=True)
                    | Q(messages__created_at__gt=F("last_read_seller"))
                ),
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        ),
    )

    # 2) "이 역할로 실제로 말을 한 적이 있는 방만" 필터
    #    (messages__sender=... 로 직접 필터하지 않고 Exists 서브쿼리 사용)
    msg_from_buyer = Message.objects.filter(
        conversation=OuterRef("pk"),
        sender=OuterRef("buyer"),
    )
    msg_from_seller = Message.objects.filter(
        conversation=OuterRef("pk"),
        sender=OuterRef("seller"),
    )
    msg_from_me = Message.objects.filter(
        conversation=OuterRef("pk"),
        sender=request.user,
    )

    if role == "seller":
        qs = qs.filter(
            post__type=Post.Type.SUPPLY,
            seller=request.user,
        ).filter(
            Exists(msg_from_buyer),   # 구매자가 실제로 말한 적 있는 방만
        )

    elif role == "buyer":
        qs = qs.filter(
            post__type=Post.Type.SUPPLY,
            buyer=request.user,
        ).filter(
            Exists(msg_from_me),      # 내가 말한 적 있는 방만
        )

    elif role == "proposer":
        qs = qs.filter(
            post__type=Post.Type.DEMAND,
            buyer=request.user,
        ).filter(
            Exists(msg_from_me),      # 내가 제안 메시지 보낸 방만
        )

    elif role == "receiver":
        qs = qs.filter(
            post__type=Post.Type.DEMAND,
            seller=request.user,
        ).filter(
            Exists(msg_from_buyer),   # 제안자가 실제로 말한 방만
        )
        # msg_from_seller 도 필요하면 추가로 쓸 수 있음

    # 3) 정렬
    qs = qs.order_by("-last_message_at", "-created_at")

    return render(request, "chat/inbox.html", {
        "conversations": qs,
        "role": role,
    })


@login_required
def complete_trade(request, conversation_id):
    conv = get_object_or_404(Conversation, pk=conversation_id)

    if request.user not in (conv.buyer, conv.seller):
        messages.error(request, "이 거래에 참여한 사용자만 완료 처리할 수 있습니다.")
        return redirect("chat:inbox")

    if request.user != conv.seller:
        messages.warning(request, "판매자만 거래 완료를 설정할 수 있습니다.")
        return redirect("chat:room", conversation_id=conv.id)

    if request.method == "POST":
        trade, created = Trade.objects.get_or_create(
            conversation=conv,
            defaults={
                "post": conv.post,
                "buyer": conv.buyer,
                "seller": conv.seller,
            },
        )
        if created:
            messages.success(request, "거래 내역에 저장되었습니다.")
        else:
            messages.info(request, "이미 거래 완료로 저장된 내역입니다.")

    return redirect("chat:room", conversation_id=conv.id)


@login_required
def cancel_trade(request, conversation_id):
    """이미 완료로 저장된 거래를 취소(삭제)"""
    conv = get_object_or_404(Conversation, pk=conversation_id)

    # 참여자만
    if request.user not in (conv.buyer, conv.seller):
        messages.error(request, "이 거래에 참여한 사용자만 취소할 수 있습니다.")
        return redirect("chat:inbox")

    # 판매자만 취소 가능
    if request.user != conv.seller:
        messages.warning(request, "판매자만 거래 취소를 할 수 있습니다.")
        return redirect("chat:room", conversation_id=conv.id)

    trade = getattr(conv, "trade", None)
    if not trade:
        messages.info(request, "아직 '거래 완료'로 저장된 내역이 없습니다.")
        return redirect("chat:room", conversation_id=conv.id)

    if request.method == "POST":
        trade.delete()
        messages.success(request, "거래 완료 상태를 취소했습니다.")
        return redirect("chat:room", conversation_id=conv.id)

    # (GET으로 직접 들어온 경우엔 그냥 방으로 돌려보내기)
    return redirect("chat:room", conversation_id=conv.id)


@login_required
def messages_json(request, conversation_id):
    conv = get_object_or_404(Conversation, pk=conversation_id)

    if request.user not in (conv.buyer, conv.seller):
        return JsonResponse({"error": "forbidden"}, status=403)

    after_id = request.GET.get("after")
    qs = conv.messages.select_related("sender")
    if after_id:
        qs = qs.filter(id__gt=after_id)

    data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": m.sender.get_username(),
            "text": m.text,
            "created": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for m in qs
    ]
    return JsonResponse({"messages": data})
