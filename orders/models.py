from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percent'
        FIXED = 'fixed', 'Fixed Amount'

    code = models.CharField(max_length=40, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENT)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    customer = models.ForeignKey('auth.User', on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    order_number = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    currency = models.ForeignKey(
        'products.Currency',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'


class OrderTrackingEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    location = models.CharField(max_length=160, blank=True)
    message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_number} -> {self.status}'


class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='carts')
    currency = models.ForeignKey(
        'products.Currency',
        on_delete=models.SET_NULL,
        related_name='carts',
        null=True,
        blank=True,
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, related_name='carts', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Cart #{self.id} for {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product'),
        ]

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
