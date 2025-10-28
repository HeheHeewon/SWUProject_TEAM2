# posts/urls.py
from django.urls import path
from .views import (
  PostListView, PostDetailView,
  DemandCreateView, SupplyCreateView,
  DemandUpdateView, SupplyUpdateView,
)

app_name = "posts"
urlpatterns = [
  path("", PostListView.as_view(), name="list"),
  path("<int:pk>/", PostDetailView.as_view(), name="detail"),
  path("demand/new/", DemandCreateView.as_view(), name="demand_new"),
  path("demand/<int:pk>/edit/", DemandUpdateView.as_view(), name="demand_edit"),
  path("supply/new/", SupplyCreateView.as_view(), name="supply_new"),
  path("supply/<int:pk>/edit/", SupplyUpdateView.as_view(), name="supply_edit"),
]
