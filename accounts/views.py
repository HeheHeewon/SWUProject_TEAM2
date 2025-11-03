from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Profile # Profile 모델 가져오기
from .forms import ProfileForm # (아래 폼은 직접 만들어야 함)

# 회원가입 뷰
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserCreationForm이 User를 저장하면 post_save 시그널로 Profile이 자동 생성됨
            return redirect('accounts:mypage') # 회원가입 성공 후 로그인 페이지로
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

# 마이페이지 뷰 (로그인 필요)
@login_required
def mypage(request):
    # 로그인한 사용자와 연결된 Profile 정보를 가져옴
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/mypage.html', {'profile': profile})

# 프로필 정보 수정 뷰 (폼은 직접 생성해야 함)
@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        # ProfileForm은 forms.py 파일에 정의해야 함
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:mypage')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})