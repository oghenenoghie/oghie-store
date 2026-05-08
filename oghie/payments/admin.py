from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('provider', 'provider_reference', 'amount', 'currency', 'status', 'user', 'created_at')
    list_filter = ('provider', 'status', 'currency')
    search_fields = ('provider_reference', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
