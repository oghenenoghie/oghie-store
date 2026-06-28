from django.db.models import Avg, Count, Q
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Category, Currency, Product, ProductImage, ProductReview, WishlistItem
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CurrencySerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
    ProductSerializer,
    WishlistItemSerializer,
)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'symbol']
    ordering_fields = ['code', 'name', 'exchange_rate_to_base']
    ordering = ['code']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'currency').prefetch_related('images').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__status=ProductReview.Status.APPROVED)),
        approved_review_count=Count('reviews', filter=Q(reviews__status=ProductReview.Status.APPROVED)),
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        is_active = self.request.query_params.get('is_active')
        in_stock = self.request.query_params.get('in_stock')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        vendor = self.request.query_params.get('vendor')
        currency = self.request.query_params.get('currency')
        min_rating = self.request.query_params.get('min_rating')

        if category:
            queryset = queryset.filter(category__slug=category)
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)
        if currency:
            queryset = queryset.filter(currency__code__iexact=currency)
        if is_active in {'true', 'false'}:
            queryset = queryset.filter(is_active=is_active == 'true')
        if in_stock in {'true', 'false'}:
            queryset = queryset.filter(stock_quantity__gt=0) if in_stock == 'true' else queryset.filter(stock_quantity=0)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_rating:
            queryset = queryset.filter(reviews__status=ProductReview.Status.APPROVED, reviews__rating__gte=min_rating).distinct()

        return queryset


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.select_related('product')
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'alt_text']
    ordering_fields = ['created_at', 'is_primary']
    ordering = ['-is_primary', 'created_at']


class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return WishlistItem.objects.select_related('product', 'product__category', 'product__currency').filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'title', 'comment', 'user__username']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = ProductReview.objects.select_related('product', 'user')
        if not self.request.user.is_staff:
            queryset = queryset.filter(status=ProductReview.Status.APPROVED)
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product__slug=product)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
