from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'username',
            'email',
            'role',
            'phone',
            'address',
            'company_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'profile']
        read_only_fields = fields
