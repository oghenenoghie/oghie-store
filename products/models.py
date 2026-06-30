from django.core.validators import FileExtensionValidator
from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=80)
    symbol = models.CharField(max_length=8, blank=True)
    exchange_rate_to_base = models.DecimalField(max_digits=12, decimal_places=6, default=1)
    is_base = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name_plural = 'currencies'

    def __str__(self):
        return self.code


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    vendor = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name='vendor_products',
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(
        upload_to='products/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return self.alt_text or f'Image for {self.product.name}'


class WishlistItem(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_wishlist_product'),
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.product.name}'


class ProductReview(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='product_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=160, blank=True)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_review'),
            models.CheckConstraint(condition=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='review_rating_1_to_5'),
        ]

    def __str__(self):
        return f'{self.product.name} review by {self.user.username}'
