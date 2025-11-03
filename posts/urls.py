# posts/urls.py
from django.urls import path
from .views import (
  PostListView, PostDetailView,
  DemandCreateView, SupplyCreateView,
  DemandUpdateView, SupplyUpdateView, DemandDeleteView, SupplyDeleteView,
)

app_name = "posts"
urlpatterns = [
  path("", PostListView.as_view(), name="list"),
  path("<int:pk>/", PostDetailView.as_view(), name="detail"),
  path("demand/new/", DemandCreateView.as_view(), name="demand_new"),
  path("demand/<int:pk>/edit/", DemandUpdateView.as_view(), name="demand_edit"),
  path("demand/<int:pk>/delete/", DemandDeleteView.as_view(), name="demand_delete"),
  path("supply/<int:pk>/delete/", SupplyDeleteView.as_view(), name="supply_delete"),
  path("supply/new/", SupplyCreateView.as_view(), name="supply_new"),
  path("supply/<int:pk>/edit/", SupplyUpdateView.as_view(), name="supply_edit"),
]
