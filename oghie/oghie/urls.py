"""
URL configuration for oghie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

admin.site.site_header = 'Oghie Store Admin'
admin.site.site_title = 'Oghie Store Admin'
admin.site.index_title = 'Dashboard'


def api_root(request):
    return JsonResponse({
        'admin': '/admin/',
        'token': '/api/auth/token/',
        'token_refresh': '/api/auth/token/refresh/',
        'current_user': '/api/auth/me/',
        'products': '/api/products/',
        'product_filters': '/api/products/?search=&category=&currency=&min_price=&max_price=&in_stock=true&min_rating=&ordering=price',
        'currencies': '/api/products/currencies/',
        'wishlist': '/api/products/wishlist/',
        'reviews': '/api/products/reviews/',
        'cart': '/api/orders/cart/active/',
        'checkout': '/api/orders/cart/{cart_id}/checkout/',
        'orders': '/api/orders/',
        'my_orders': '/api/orders/mine/',
        'order_tracking': '/api/orders/tracking/',
        'payments': '/api/payments/',
        'cms_sections': '/api/cms/sections/',
        'analytics': '/api/analytics/summary/',
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('api/auth/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/cms/', include('cms.urls')),
    path('api/analytics/', include('orders.analytics_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
