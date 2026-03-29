from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.core.paginator import Paginator  # DualListView 쓰면 사용 가능

from guides.models import Guide
from .models import Post
from .forms import DemandForm, SupplyForm

# ─────────────────────────────────────────────────────────
# (홈 섹션) 뉴스 목업
# ─────────────────────────────────────────────────────────
NEWS_ITEMS = [
    {
        "title": "버려지던 커피 찌꺼기를 자원으로…강동구, '커피찌꺼기 재활용 캠페인' 본격 추진",
        "url": "https://www.seoulcity.co.kr/news/articleView.html?idxno=501146",
        "img": "img/news/article4.png",
        "date": "2025.09.18",
    },
    {
        "title": "커피 찌꺼기, 문 앞에 놔두세요. 재활용합니다",
        "url": "https://www.khan.co.kr/article/202503131338001",
        "img": "img/news/article1.png",
        "date": "2025.03.13",
    },
    {
        "title": "스타벅스, 커피 퇴비 농가 지원 5500톤 돌파",
        "url": "https://www.chosun.com/economy/market_trend/2025/07/15/KWR7HQGCNFE4RD5IACNYHVD3LM/",
        "img": "img/news/article2.png",
        "date": "2025.07.15",
    },
    {
        "title": "[브랜드이슈] 업사이클링 브랜드 '커피어게인', 커피찌꺼기 활용한 신제품 내달 출시",
        "url": "https://www.sisunnews.co.kr/news/articleView.html?idxno=158314",
        "img": "img/news/article3.png",
        "date": "2022.02.21",
    },
]

# ─────────────────────────────────────────────────────────
# 공용 목록/상세
# ─────────────────────────────────────────────────────────
class PostListView(ListView):
    model = Post
    template_name = "posts/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET

        t = q.get("type")
        if t in (Post.Type.DEMAND, Post.Type.SUPPLY):
            qs = qs.filter(type=t)

        if (u := q.get("usage")):
            qs = qs.filter(usage=u)

        if (d := q.get("dry")) in ("true", "false"):
            qs = qs.filter(dry=(d == "true"))

        if (p := q.get("package")):
            qs = qs.filter(package=p)

        if (pt := q.get("price_type")):
            qs = qs.filter(price_type=pt)

        return qs


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detail.html"

# ─────────────────────────────────────────────────────────
# 생성/수정/삭제
# ─────────────────────────────────────────────────────────
class DemandCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/new_demand.html"
    success_url = reverse_lazy("posts:browse_demand")

    def form_valid(self, form):
        form.instance.type = Post.Type.DEMAND
        form.instance.author = self.request.user
        form.instance.price = None  # 수요글은 실제 거래가 금지
        form.instance.price_type = form.instance.demand_price_pref
        return super().form_valid(form)


class SupplyCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = SupplyForm
    template_name = "posts/new_supply.html"
    success_url = reverse_lazy("posts:browse")

    def form_valid(self, form):
        form.instance.type = Post.Type.SUPPLY
        form.instance.author = self.request.user
        return super().form_valid(form)


class AuthorOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author_id == self.request.user.id


class DemandUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/edit_demand.html"

    def form_valid(self, form):
        form.instance.type = Post.Type.DEMAND
        form.instance.price = None
        form.instance.price_type = form.instance.demand_price_pref
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("posts:detail", args=[self.object.pk])


class SupplyUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = SupplyForm
    template_name = "posts/edit_supply.html"

    def form_valid(self, form):
        form.instance.type = Post.Type.SUPPLY
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("posts:detail", args=[self.object.pk])


class DemandDeleteView(LoginRequiredMixin, AuthorOnlyMixin, DeleteView):
    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("home")


class SupplyDeleteView(LoginRequiredMixin, AuthorOnlyMixin, DeleteView):
    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("home")

# ─────────────────────────────────────────────────────────
# 홈
# ─────────────────────────────────────────────────────────
def home(request):
    demand_posts = (
        Post.objects.filter(type=Post.Type.DEMAND)
        .select_related("author")
        .order_by("-created_at")[:4]
    )
    NEWS_COUNT = 4
    news_items = NEWS_ITEMS[:NEWS_COUNT]

    guides = (
        Guide.objects.filter(is_published=True)
        .select_related("author")
        .prefetch_related("steps")[:4]
    )

    return render(
        request,
        "home.html",
        {
            "demand_posts": demand_posts,
            "news_items": news_items,
            "guides": guides,
        },
    )

# ─────────────────────────────────────────────────────────
# 전용 목록: 공급 / 수요
# ─────────────────────────────────────────────────────────
class SupplyOnlyListView(ListView):
    """
    공급글만 모아서 보여주는 전용 목록.
    템플릿은 posts/list.html 공용을 쓰고, only_supply 플래그로 카드 모양 분기.
    """
    model = Post
    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return (
            Post.objects.filter(type=Post.Type.SUPPLY)
            .select_related("author")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "판매자 상품 둘러보기"
        ctx["only_supply"] = True
        return ctx


class DemandOnlyListView(ListView):
    """
    수요글만 모아서 보여주는 전용 목록.
    usage(퇴비/공예용/연구/실험/기타) GET 파라미터로도 필터.
    """
    model = Post
    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Post.objects.filter(type=Post.Type.DEMAND)
            .select_related("author")
            .order_by("-created_at")
        )

        usage = self.request.GET.get("usage")
        if usage:
            qs = qs.filter(usage=usage)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "이런 커피를 찾아요!"
        ctx["only_demand"] = True
        ctx["current_usage"] = self.request.GET.get("usage", "")
        return ctx


class DualListView(TemplateView):
    """
    좌측: 수요글, 우측: 공급글을 한 화면에서 동시 표기.
    (지금은 간단 버전 – 필요하면 Paginator로 양쪽 따로 페이지네이션도 가능)
    """
    template_name = "posts/list_dual.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "게시글"
        ctx["demand_posts"] = (
            Post.objects.filter(type=Post.Type.DEMAND)
            .select_related("author")
            .order_by("-created_at")
        )
        ctx["supply_posts"] = (
            Post.objects.filter(type=Post.Type.SUPPLY)
            .select_related("author")
            .order_by("-created_at")
        )
        return ctx
