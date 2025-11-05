# posts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse             # ✅ reverse 추가
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from .forms import DemandForm, SupplyForm

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
        "img": "img/news/article1.png",     # ← static 기준 경로
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
    # 필요하면 계속 추가…
]

class PostListView(ListView):
    model = Post
    template_name = "posts/list.html"
    paginate_by = 20  # ✅ 주석으로

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

class DemandCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/new_demand.html"
    # 상세로 보내고 싶으면 get_success_url로 통일해도 됨
    success_url = reverse_lazy("posts:list")

    def form_valid(self, form):
        form.instance.type = Post.Type.DEMAND
        form.instance.author = self.request.user
        # 수요글: 실제 거래가 금지 -> 확실히 None
        form.instance.price = None
        # 수요글: 사용자가 고른 지불 의사(demand_price_pref)를 모델의 price_type에도 반영
        # (price_type 필드가 공통 필수이므로 일관성 보장)
        form.instance.price_type = form.instance.demand_price_pref
        return super().form_valid(form)

class SupplyCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = SupplyForm
    template_name = "posts/new_supply.html"
    success_url = reverse_lazy("posts:list")

    def form_valid(self, form):
        form.instance.type = Post.Type.SUPPLY
        form.instance.author = self.request.user
        return super().form_valid(form)

class AuthorOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author_id == self.request.user.id

# ✅ UpdateView는 상세로 리다이렉트
class DemandUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/edit_demand.html"

    def form_valid(self, form):
        # 업데이트 시에도 동일한 규칙 유지
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
    success_url = reverse_lazy("posts:list")

class SupplyDeleteView(LoginRequiredMixin, AuthorOnlyMixin, DeleteView):
    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("posts:list")

def home(request):
    demand_posts = (
        Post.objects.filter(type=Post.Type.DEMAND)
        .select_related("author")
        .order_by("-created_at")[:8]
    )
    # 보여줄 뉴스 개수 설정 (6~8 중 택1)
    NEWS_COUNT = 4 # 또는 8
    news_items = NEWS_ITEMS[:NEWS_COUNT]  # 앞에서 원하는 개수만

    return render(request,
                  "home.html",
            {
                      "demand_posts": demand_posts,
                      "news_items": news_items,  # ← 추가
                    },
                  )

