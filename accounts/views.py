# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from chat.models import Trade
from posts.models import Post
from .forms import SignUpForm, ProfileForm
from .models import Profile

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # accounts.User로 저장
            # 시그널로 Profile 자동 생성됨. 혹시 없으면 안전망:
            Profile.objects.get_or_create(user=user)
            login(request, user)         # 가입 즉시 로그인
            return redirect("accounts:mypage")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def mypage(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)


    # ✅ 내가 작성한 모든 글 (공급글 + 수요글)
    my_posts = (
        Post.objects
        .filter(author=request.user)
        .order_by("-created_at")
    )

    # ✅ 내가 '구매자'로 참여한 거래만 가져오기
    bought_trades = (
        Trade.objects
        .filter(buyer=request.user)
        .select_related("post", "seller")
        .order_by("-created_at")
    )

    # ✅ 내가 '판매자'로 참여한 거래
    sold_trades = (
        Trade.objects
        .filter(seller=request.user)
        .select_related("post", "buyer")
        .order_by("-created_at")
    )

    return render(request, "accounts/mypage.html", {
        "profile": profile,
        "my_posts": my_posts,
        "bought_trades": bought_trades,
        "sold_trades": sold_trades,
    })


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:mypage")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"form": form})
