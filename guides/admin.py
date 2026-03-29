from django.contrib import admin
from .models import Guide, GuideStep

class GuideStepInline(admin.TabularInline):
    model = GuideStep
    extra = 1

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at")
    list_filter  = ("is_published",)
    search_fields = ("title", "summary", "author__username")
    inlines = [GuideStepInline]

@admin.register(GuideStep)
class GuideStepAdmin(admin.ModelAdmin):
    list_display = ("guide", "order", "title", "icon")
    list_editable = ("order",)
