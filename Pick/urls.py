# Pick/urls.py
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView  # 홈(랜딩)용
from django.contrib.auth import views as auth_views    # 커스텀 로그인 템플릿용
from posts import views as post_views   # ✅ 추가

from posts.views import home

urlpatterns = [
    # 홈(랜딩) — 최상단에 노출
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', post_views.home, name='home'),

    path('admin/', admin.site.urls),
    # 계정(여기 안에 login/logout/password change/reset 전부 포함됨)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # 선택: 루트 단축 경로(/login, /signup, /mypage → /accounts/...)
    path('login/', RedirectView.as_view(url=reverse_lazy('accounts:login'), permanent=False)),
    path('signup/', RedirectView.as_view(url=reverse_lazy('accounts:signup'), permanent=False)),
    path('mypage/', RedirectView.as_view(url=reverse_lazy('accounts:mypage'), permanent=False)),

    path('cart/', include('cart.urls')),  # accounts/urls.py가 있어야 함
    path('posts/', include('posts.urls', namespace='posts')),
]
