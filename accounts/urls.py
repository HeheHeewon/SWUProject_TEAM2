# accounts/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # ① 커스텀 로그인(템플릿 지정) — 먼저 둠 (경로: /accounts/login/)
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),

    # ② 기본 인증 라우트 세트(로그아웃/비번변경/리셋 등)
    path('', include('django.contrib.auth.urls')),

    # ③ 회원가입/마이페이지
    path('signup/', views.signup, name='signup'),
    path('mypage/', views.mypage, name='mypage'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
