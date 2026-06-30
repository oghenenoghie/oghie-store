from rest_framework import serializers

from .models import CMSSection


class CMSSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSSection
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
