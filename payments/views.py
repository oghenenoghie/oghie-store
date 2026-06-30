from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('user')
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['provider', 'provider_reference', 'status', 'user__username', 'user__email']
    ordering_fields = ['amount', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
