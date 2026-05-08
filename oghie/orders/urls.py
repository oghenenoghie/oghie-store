from rest_framework.routers import DefaultRouter

from .views import (
    CartItemViewSet,
    CartViewSet,
    CouponViewSet,
    MyOrderViewSet,
    OrderItemViewSet,
    OrderTrackingEventViewSet,
    OrderViewSet,
)

app_name = 'orders'

router = DefaultRouter()
router.register('cart/items', CartItemViewSet, basename='cart-item')
router.register('cart', CartViewSet, basename='cart')
router.register('coupons', CouponViewSet, basename='coupon')
router.register('items', OrderItemViewSet, basename='order-item')
router.register('mine', MyOrderViewSet, basename='my-order')
router.register('tracking', OrderTrackingEventViewSet, basename='order-tracking')
router.register('', OrderViewSet, basename='order')

urlpatterns = router.urls
