from django.contrib import admin

from .models import Cart, CartItem, Coupon, Order, OrderItem, OrderTrackingEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderTrackingEventInline(admin.TabularInline):
    model = OrderTrackingEvent
    extra = 0


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'grand_total', 'currency', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline, OrderTrackingEventInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'line_total')
    search_fields = ('order__order_number', 'product_name')


@admin.register(OrderTrackingEvent)
class OrderTrackingEventAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'location', 'message', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'location', 'message')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'coupon', 'is_active', 'updated_at')
    list_filter = ('is_active', 'currency')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'updated_at')
    search_fields = ('cart__user__username', 'product__name')
