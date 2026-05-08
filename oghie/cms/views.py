from rest_framework import filters, viewsets

from products.permissions import IsAdminOrReadOnly

from .models import CMSSection
from .serializers import CMSSectionSerializer


class CMSSectionViewSet(viewsets.ModelViewSet):
    queryset = CMSSection.objects.all()
    serializer_class = CMSSectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'body', 'section_type']
    ordering_fields = ['sort_order', 'created_at', 'updated_at']
    ordering = ['sort_order', 'title']
