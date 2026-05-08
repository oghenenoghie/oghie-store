from rest_framework import serializers

from .models import Category, Currency, Product, ProductImage, ProductReview, WishlistItem


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            'id',
            'code',
            'name',
            'symbol',
            'exchange_rate_to_base',
            'is_base',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
            'alt_text',
            'is_primary',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'vendor',
            'category',
            'category_detail',
            'name',
            'slug',
            'description',
            'price',
            'currency',
            'currency_detail',
            'stock_quantity',
            'is_active',
            'images',
            'average_rating',
            'review_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        approved_reviews = obj.reviews.filter(status=ProductReview.Status.APPROVED)
        if not approved_reviews.exists():
            return None
        total = sum(review.rating for review in approved_reviews)
        return round(total / approved_reviews.count(), 2)

    def get_review_count(self, obj):
        return obj.reviews.filter(status=ProductReview.Status.APPROVED).count()


class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'user', 'product', 'product_detail', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            'id',
            'user',
            'username',
            'product',
            'rating',
            'title',
            'comment',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']
