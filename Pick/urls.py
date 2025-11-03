# Pick/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView         # 홈(랜딩)용
from django.contrib.auth import views as auth_views    # 커스텀 로그인 템플릿용

urlpatterns = [
    # ✅ 홈(랜딩) — 최상단에 노출
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),  # accounts/urls.py가 있어야 함
=======

    # ✅ 커스텀 템플릿을 쓰는 로그인 (registration/login.html 대신 accounts/login.html 사용)
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='accounts/login.html'),
         name='login'),

    # ✅ 기본 인증 URL 세트 (logout, password_change, reset 등)
    path('accounts/', include('django.contrib.auth.urls')),

    # ✅ 게시글 앱
    path('posts/', include('posts.urls', namespace='posts')),
>>>>>>> TRY1
]
