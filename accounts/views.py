# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
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
    return render(request, "accounts/mypage.html", {"profile": profile})

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
