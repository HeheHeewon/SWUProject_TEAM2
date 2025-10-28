# posts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Post
from .forms import DemandForm, SupplyForm
# 거리 계산 제거: from common.geo import haversine_km  # ← 사용 안 함

class PostListView(ListView):
    model = Post
    template_name = "posts/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET

        # type 필터(수요/공급)
        t = q.get("type")
        if t in (Post.Type.DEMAND, Post.Type.SUPPLY):
            qs = qs.filter(type=t)

        # 수요글 필터
        if (u := q.get("usage")):
            qs = qs.filter(usage=u)
        if (d := q.get("dry")) in ("true", "false"):
            qs = qs.filter(dry=(d == "true"))
        if (p := q.get("package")):
            qs = qs.filter(package=p)
        if (pt := q.get("price_type")):
            qs = qs.filter(price_type=pt)

        # 거리 필터는 사용하지 않음
        # withinKm, lat, lng 파라미터는 무시합니다.

        return qs

class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detail.html"

class DemandCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/new_demand.html"
    success_url = reverse_lazy("posts:list")

    def form_valid(self, form):
        form.instance.type = Post.Type.DEMAND
        form.instance.author = self.request.user
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

class DemandUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = DemandForm
    template_name = "posts/edit_demand.html"
    success_url = reverse_lazy("posts:list")

class SupplyUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = SupplyForm
    template_name = "posts/edit_supply.html"
    success_url = reverse_lazy("posts:list")
