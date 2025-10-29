# posts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse             # ✅ reverse 추가
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from .forms import DemandForm, SupplyForm

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
    def get_success_url(self):
        return reverse("posts:detail", args=[self.object.pk])

class SupplyUpdateView(LoginRequiredMixin, AuthorOnlyMixin, UpdateView):
    model = Post
    form_class = SupplyForm
    template_name = "posts/edit_supply.html"
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
