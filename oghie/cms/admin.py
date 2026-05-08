from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CMSSection


@admin.register(CMSSection)
class CMSSectionAdmin(ModelAdmin):
    list_display = ('title', 'section_type', 'sort_order', 'is_active', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('title', 'slug', 'body')
    prepopulated_fields = {'slug': ('title',)}
