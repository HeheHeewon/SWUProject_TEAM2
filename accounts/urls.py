from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Django 기본 인증 뷰 가져오기

app_name = 'accounts'

urlpatterns = [
    # 로그인 / 로그아웃 
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 회원가입
    path('signup/', views.signup, name='signup'),
    
    # 마이페이지
    path('mypage/', views.mypage, name='mypage'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]