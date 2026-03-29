from django.views.generic import ListView, DetailView
from guides.models import Guide, GuideStep

class GuideListView(ListView):
    template_name = "guides/list.html"
    context_object_name = "guides"
    paginate_by = 12

    def get_queryset(self):
        return (Guide.objects.filter(is_published=True)
                .select_related("author")
                .prefetch_related("steps"))

class GuideDetailView(DetailView):
    model = Guide
    template_name = "guides/detail.html"
