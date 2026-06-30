from django.db import models


class CMSSection(models.Model):
    class SectionType(models.TextChoices):
        HERO = 'hero', 'Hero'
        BANNER = 'banner', 'Banner'
        FEATURED_PRODUCTS = 'featured_products', 'Featured Products'
        CONTENT = 'content', 'Content'
        FOOTER = 'footer', 'Footer'

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    section_type = models.CharField(max_length=40, choices=SectionType.choices, default=SectionType.CONTENT)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to='cms/', blank=True)
    link_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title
