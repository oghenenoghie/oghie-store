from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CurrencyViewSet,
    ProductImageViewSet,
    ProductReviewViewSet,
    ProductViewSet,
    WishlistItemViewSet,
)

app_name = 'products'

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('currencies', CurrencyViewSet, basename='currency')
router.register('images', ProductImageViewSet, basename='product-image')
router.register('reviews', ProductReviewViewSet, basename='product-review')
router.register('wishlist', WishlistItemViewSet, basename='wishlist-item')
router.register('', ProductViewSet, basename='product')

urlpatterns = router.urls
