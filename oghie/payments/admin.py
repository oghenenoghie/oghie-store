from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('provider', 'provider_reference', 'amount', 'currency', 'status', 'user', 'created_at')
    list_filter = ('provider', 'status', 'currency')
    search_fields = ('provider_reference', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
