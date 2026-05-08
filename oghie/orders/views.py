from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from django.utils.crypto import get_random_string
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from products.models import Product
from users.models import UserProfile

from .models import Cart, CartItem, Coupon, Order, OrderItem, OrderTrackingEvent
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    CouponSerializer,
    OrderItemSerializer,
    OrderSerializer,
    OrderTrackingEventSerializer,
)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'description']
    ordering_fields = ['code', 'created_at', 'expires_at']
    ordering = ['code']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer', 'coupon').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer__username', 'customer__email', 'status']
    ordering_fields = ['created_at', 'updated_at', 'grand_total']
    ordering = ['-created_at']


class MyOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'status']
    ordering_fields = ['created_at', 'updated_at', 'grand_total']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.select_related('customer', 'coupon', 'currency').prefetch_related('items', 'tracking_events').filter(customer=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'product')
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order__order_number', 'product_name']
    ordering_fields = ['quantity', 'unit_price', 'line_total']


class OrderTrackingEventViewSet(viewsets.ModelViewSet):
    queryset = OrderTrackingEvent.objects.select_related('order')
    serializer_class = OrderTrackingEventSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order__order_number', 'status', 'location', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        return Response(self.get_serializer(cart).data)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=400)

        with transaction.atomic():
            subtotal = sum((item.product.price * item.quantity for item in cart.items.select_related('product')), Decimal('0.00'))
            discount_total = Decimal('0.00')
            if cart.coupon:
                if cart.coupon.discount_type == Coupon.DiscountType.PERCENT:
                    discount_total = subtotal * cart.coupon.discount_value / Decimal('100')
                else:
                    discount_total = min(cart.coupon.discount_value, subtotal)

            order = Order.objects.create(
                customer=request.user,
                order_number=f'OGH-{get_random_string(10).upper()}',
                status=Order.Status.PENDING,
                coupon=cart.coupon,
                currency=cart.currency,
                subtotal=subtotal,
                discount_total=discount_total,
                grand_total=subtotal - discount_total,
                shipping_address=serializer.validated_data.get('shipping_address', ''),
                billing_address=serializer.validated_data.get('billing_address', ''),
                notes=serializer.validated_data.get('notes', ''),
            )

            for item in cart.items.select_related('product'):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    unit_price=item.product.price,
                    quantity=item.quantity,
                    line_total=item.product.price * item.quantity,
                )

            OrderTrackingEvent.objects.create(
                order=order,
                status=Order.Status.PENDING,
                message='Order placed',
            )
            cart.is_active = False
            cart.save(update_fields=['is_active', 'updated_at'])

        return Response(OrderSerializer(order).data, status=201)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.select_related('cart', 'product').filter(cart__user=self.request.user, cart__is_active=True)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        serializer.save(cart=cart)


class AnalyticsSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders_by_status = dict(Order.objects.values_list('status').annotate(total=Count('id')))
        payments_by_status = dict(Payment.objects.values_list('status').annotate(total=Count('id')))
        revenue = Order.objects.filter(status__in=[Order.Status.PAID, Order.Status.PROCESSING, Order.Status.SHIPPED, Order.Status.DELIVERED]).aggregate(total=Sum('grand_total'))['total'] or 0

        return Response({
            'totals': {
                'products': Product.objects.count(),
                'orders': Order.objects.count(),
                'customers': UserProfile.objects.filter(role=UserProfile.Role.CUSTOMER).count(),
                'vendors': UserProfile.objects.filter(role=UserProfile.Role.VENDOR).count(),
                'revenue': revenue,
            },
            'charts': {
                'orders_by_status': orders_by_status,
                'payments_by_status': payments_by_status,
                'top_products': list(
                    OrderItem.objects.values('product_name')
                    .annotate(quantity=Sum('quantity'), revenue=Sum('line_total'))
                    .order_by('-quantity')[:10]
                ),
                'orders_over_time': list(
                    Order.objects.extra({'date': "date(created_at)"})
                    .values('date')
                    .annotate(total=Count('id'), revenue=Sum('grand_total'))
                    .order_by('date')[:30]
                ),
            },
        })
