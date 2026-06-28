from decimal import Decimal

from rest_framework import serializers

from .models import Cart, CartItem, Coupon, Order, OrderItem, OrderTrackingEvent


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'unit_price', 'quantity', 'line_total']
        read_only_fields = ['id']


class OrderTrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTrackingEvent
        fields = ['id', 'order', 'status', 'location', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_events = OrderTrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'order_number',
            'status',
            'coupon',
            'currency',
            'subtotal',
            'discount_total',
            'shipping_total',
            'tax_total',
            'grand_total',
            'shipping_address',
            'billing_address',
            'notes',
            'items',
            'tracking_events',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'unit_price', 'quantity', 'line_total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'cart', 'created_at', 'updated_at']

    def get_line_total(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    discount_total = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'currency', 'coupon', 'is_active', 'items', 'subtotal', 'discount_total', 'grand_total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_active', 'created_at', 'updated_at']

    def _compute_totals(self, obj):
        subtotal = sum((item.product.price * item.quantity for item in obj.items.all()), Decimal('0.00'))
        if obj.coupon:
            if obj.coupon.discount_type == Coupon.DiscountType.PERCENT:
                discount = subtotal * obj.coupon.discount_value / Decimal('100')
            else:
                discount = min(obj.coupon.discount_value, subtotal)
        else:
            discount = Decimal('0.00')
        return subtotal, discount

    def get_subtotal(self, obj):
        subtotal, _ = self._compute_totals(obj)
        return subtotal

    def get_discount_total(self, obj):
        _, discount = self._compute_totals(obj)
        return discount

    def get_grand_total(self, obj):
        subtotal, discount = self._compute_totals(obj)
        return subtotal - discount


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
