import io
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from cms.models import CMSSection
from orders.models import Cart, CartItem, Coupon, Order, OrderItem, OrderTrackingEvent
from payments.models import Payment
from products.models import Category, Currency, Product, ProductImage, ProductReview, WishlistItem
from users.models import UserProfile

try:
    from PIL import Image
except ImportError:
    Image = None


CATEGORIES = [
    ('Sneakers', 'Everyday and performance sneakers for every occasion.'),
    ('Apparel', 'Shirts, hoodies, and outerwear for a modern wardrobe.'),
    ('Accessories', 'Bags, belts, and small goods to complete the look.'),
    ('Electronics', 'Gadgets and audio gear for the home and on the go.'),
    ('Home & Living', 'Décor and essentials for a comfortable home.'),
    ('Beauty', 'Skincare and grooming products.'),
]

PRODUCT_NAMES = {
    'Sneakers': ['Cloudrunner Trainer', 'Urban Glide Sneaker', 'Trailblazer Hiker'],
    'Apparel': ['Essential Cotton Hoodie', 'Lightweight Bomber Jacket', 'Classic Crew Tee'],
    'Accessories': ['Leather Weekender Bag', 'Woven Canvas Belt', 'Minimalist Wallet'],
    'Electronics': ['Wireless Noise-Cancel Headphones', 'Portable Bluetooth Speaker', 'Smart Fitness Band'],
    'Home & Living': ['Ceramic Pour-Over Set', 'Linen Throw Blanket', 'Scented Soy Candle'],
    'Beauty': ['Vitamin C Face Serum', 'Sandalwood Beard Oil', 'Hydrating Lip Balm Trio'],
}

VENDORS = [
    ('vendor_ada', 'Ada', 'Okoye', 'vendor.ada@oghiestore.test'),
    ('vendor_femi', 'Femi', 'Balogun', 'vendor.femi@oghiestore.test'),
    ('vendor_zainab', 'Zainab', 'Bello', 'vendor.zainab@oghiestore.test'),
]

CUSTOMERS = [
    ('customer_chidi', 'Chidi', 'Eze', 'chidi@oghiestore.test'),
    ('customer_amara', 'Amara', 'Nwosu', 'amara@oghiestore.test'),
    ('customer_tunde', 'Tunde', 'Ade', 'tunde@oghiestore.test'),
    ('customer_grace', 'Grace', 'Udo', 'grace@oghiestore.test'),
    ('customer_kemi', 'Kemi', 'Fashola', 'kemi@oghiestore.test'),
]

COLORS = [
    (232, 93, 4), (4, 141, 232), (34, 139, 87), (176, 38, 255),
    (232, 4, 62), (255, 176, 0), (0, 168, 168), (120, 120, 120),
]


class Command(BaseCommand):
    help = 'Seeds the database with demo content for local/testing use (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete previously seeded demo data before reseeding.',
        )

    def handle(self, *args, **options):
        random.seed(42)

        if options['flush']:
            self._flush()

        currency_map = {c.code: c for c in Currency.objects.all()}
        usd = currency_map.get('USD') or Currency.objects.filter(is_base=True).first()

        vendors = self._seed_users(VENDORS, UserProfile.Role.VENDOR)
        customers = self._seed_users(CUSTOMERS, UserProfile.Role.CUSTOMER)

        categories = self._seed_categories()
        products = self._seed_products(categories, vendors, usd)
        self._seed_reviews(products, customers)
        self._seed_wishlists(products, customers)
        self._seed_cms_sections(products)
        coupons = self._seed_coupons()
        self._seed_orders(products, customers, coupons, usd)
        self._seed_carts(products, customers, usd)

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))

    def _flush(self):
        self.stdout.write('Flushing previously seeded demo data...')
        usernames = [u for u, *_ in VENDORS + CUSTOMERS]
        Order.objects.filter(order_number__startswith='DEMO-').delete()
        Coupon.objects.filter(code__startswith='DEMO').delete()
        CMSSection.objects.filter(slug__startswith='demo-').delete()
        Product.objects.filter(slug__startswith='demo-').delete()
        Category.objects.filter(name__in=[c for c, _ in CATEGORIES]).delete()
        User.objects.filter(username__in=usernames).delete()

    def _seed_users(self, roster, role):
        users = []
        for username, first, last, email in roster:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password('DemoPass123!')
                user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.phone = profile.phone or f'+234800{random.randint(1000000, 9999999)}'
            profile.address = profile.address or f'{random.randint(1, 200)} Independence Way, Lagos, Nigeria'
            if role == UserProfile.Role.VENDOR:
                profile.company_name = profile.company_name or f'{first} {last} Trading Co.'
            profile.save()
            users.append(user)
        return users

    def _placeholder_image(self, label):
        if Image is None:
            return None
        color = random.choice(COLORS)
        img = Image.new('RGB', (600, 600), color=color)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return ContentFile(buf.getvalue(), name=f'{label}.png')

    def _seed_categories(self):
        categories = {}
        for i, (name, description) in enumerate(CATEGORIES):
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': name.lower().replace(' & ', '-').replace(' ', '-'),
                    'description': description,
                    'is_active': True,
                },
            )
            categories[name] = category
        return categories

    def _seed_products(self, categories, vendors, currency):
        products = []
        for cat_name, names in PRODUCT_NAMES.items():
            category = categories[cat_name]
            for name in names:
                slug = 'demo-' + name.lower().replace(' ', '-').replace('&', 'and')
                vendor = random.choice(vendors)
                price = round(random.uniform(15, 250), 2)
                product, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'vendor': vendor,
                        'category': category,
                        'name': name,
                        'description': (
                            f'{name} from our {cat_name} collection. Crafted for everyday '
                            'reliability with a focus on comfort and durability.'
                        ),
                        'price': price,
                        'currency': currency,
                        'stock_quantity': random.randint(0, 120),
                        'is_active': True,
                    },
                )
                if created:
                    for i in range(2):
                        image_file = self._placeholder_image(f'{slug}-{i}')
                        if image_file is None:
                            continue
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            alt_text=f'{name} view {i + 1}',
                            is_primary=(i == 0),
                        )
                products.append(product)
        return products

    def _seed_reviews(self, products, customers):
        titles = ['Great value', 'Exactly as described', 'Would buy again', 'Good but slow shipping', 'Solid quality']
        comments = [
            'Really happy with this purchase, fits perfectly and looks great.',
            'Shipping took a bit longer than expected but the product is solid.',
            'Exceeded my expectations, will be ordering more.',
            'Decent quality for the price point.',
            'Matches the photos exactly, very satisfied.',
        ]
        for product in products:
            reviewers = random.sample(customers, k=min(2, len(customers)))
            for customer in reviewers:
                ProductReview.objects.get_or_create(
                    user=customer,
                    product=product,
                    defaults={
                        'rating': random.randint(3, 5),
                        'title': random.choice(titles),
                        'comment': random.choice(comments),
                        'status': random.choice(
                            [ProductReview.Status.APPROVED, ProductReview.Status.APPROVED, ProductReview.Status.PENDING]
                        ),
                    },
                )

    def _seed_wishlists(self, products, customers):
        for customer in customers:
            picks = random.sample(products, k=min(3, len(products)))
            for product in picks:
                WishlistItem.objects.get_or_create(user=customer, product=product)

    def _seed_cms_sections(self, products):
        sections = [
            ('demo-hero-main', 'Summer Refresh Is Here', CMSSection.SectionType.HERO,
             'Discover new arrivals across sneakers, apparel, and accessories.', 1),
            ('demo-banner-sale', '20% Off Sitewide This Week', CMSSection.SectionType.BANNER,
             'Use code DEMOSAVE20 at checkout.', 2),
            ('demo-featured', 'Featured Products', CMSSection.SectionType.FEATURED_PRODUCTS,
             'Hand-picked favorites from our vendors.', 3),
            ('demo-content-about', 'About Oghie Store', CMSSection.SectionType.CONTENT,
             'Oghie Store connects independent vendors with customers across Nigeria and beyond.', 4),
            ('demo-content-shipping', 'Shipping & Returns', CMSSection.SectionType.CONTENT,
             'Free shipping on orders over $50. Returns accepted within 30 days.', 5),
            ('demo-footer-main', 'Store Footer', CMSSection.SectionType.FOOTER,
             'Oghie Store — quality goods from trusted vendors.', 6),
        ]
        for slug, title, section_type, body, order in sections:
            CMSSection.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'section_type': section_type,
                    'body': body,
                    'sort_order': order,
                    'is_active': True,
                },
            )

    def _seed_coupons(self):
        coupons_data = [
            ('DEMOSAVE20', Coupon.DiscountType.PERCENT, 20, 100),
            ('DEMOFLAT10', Coupon.DiscountType.FIXED, 10, 200),
            ('DEMOWELCOME', Coupon.DiscountType.PERCENT, 15, None),
        ]
        coupons = []
        for code, dtype, value, limit in coupons_data:
            coupon, _ = Coupon.objects.get_or_create(
                code=code,
                defaults={
                    'description': f'Demo coupon: {value}{"%" if dtype == Coupon.DiscountType.PERCENT else " off"}',
                    'discount_type': dtype,
                    'discount_value': value,
                    'usage_limit': limit,
                    'is_active': True,
                },
            )
            coupons.append(coupon)
        return coupons

    def _seed_orders(self, products, customers, coupons, currency):
        statuses = [
            Order.Status.DELIVERED, Order.Status.SHIPPED, Order.Status.PROCESSING,
            Order.Status.PAID, Order.Status.PENDING, Order.Status.CANCELLED,
        ]
        for i, customer in enumerate(customers):
            for j in range(2):
                order_number = f'DEMO-{1000 + i * 10 + j}'
                if Order.objects.filter(order_number=order_number).exists():
                    continue
                items_source = random.sample(products, k=min(3, len(products)))
                subtotal = sum(p.price for p in items_source)
                coupon = random.choice(coupons) if random.random() > 0.5 else None
                discount = round(float(subtotal) * 0.1, 2) if coupon else 0
                shipping = 5.99
                tax = round(float(subtotal) * 0.05, 2)
                grand_total = round(float(subtotal) - discount + shipping + tax, 2)
                status = random.choice(statuses)

                order = Order.objects.create(
                    customer=customer,
                    order_number=order_number,
                    status=status,
                    coupon=coupon,
                    currency=currency,
                    subtotal=subtotal,
                    discount_total=discount,
                    shipping_total=shipping,
                    tax_total=tax,
                    grand_total=grand_total,
                    shipping_address=f'{customer.profile.address}',
                    billing_address=f'{customer.profile.address}',
                    notes='',
                )
                order.created_at = timezone.now() - timedelta(days=random.randint(1, 60))
                order.save(update_fields=['created_at'])

                for product in items_source:
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=qty,
                        line_total=round(float(product.price) * qty, 2),
                    )

                progression = {
                    Order.Status.PENDING: [Order.Status.PENDING],
                    Order.Status.PAID: [Order.Status.PENDING, Order.Status.PAID],
                    Order.Status.PROCESSING: [Order.Status.PENDING, Order.Status.PAID, Order.Status.PROCESSING],
                    Order.Status.SHIPPED: [Order.Status.PENDING, Order.Status.PAID, Order.Status.PROCESSING, Order.Status.SHIPPED],
                    Order.Status.DELIVERED: [
                        Order.Status.PENDING, Order.Status.PAID, Order.Status.PROCESSING,
                        Order.Status.SHIPPED, Order.Status.DELIVERED,
                    ],
                    Order.Status.CANCELLED: [Order.Status.PENDING, Order.Status.CANCELLED],
                }.get(status, [status])
                for step in progression:
                    OrderTrackingEvent.objects.create(
                        order=order,
                        status=step,
                        location='Lagos Fulfillment Center',
                        message=f'Order marked as {step}.',
                    )

                if status in (Order.Status.PAID, Order.Status.PROCESSING, Order.Status.SHIPPED, Order.Status.DELIVERED):
                    Payment.objects.get_or_create(
                        provider_reference=f'{order_number}-PAY',
                        defaults={
                            'user': customer,
                            'provider': random.choice(['stripe', 'paystack', 'flutterwave']),
                            'amount': grand_total,
                            'currency': currency.code if currency else 'USD',
                            'status': Payment.Status.PAID,
                            'metadata': {'order_number': order_number},
                        },
                    )

    def _seed_carts(self, products, customers, currency):
        for customer in customers[:3]:
            cart, _ = Cart.objects.get_or_create(
                user=customer,
                is_active=True,
                defaults={'currency': currency},
            )
            picks = random.sample(products, k=min(2, len(products)))
            for product in picks:
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': random.randint(1, 2)},
                )
