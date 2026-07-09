from rest_framework import serializers

from .models import CMSSection


class CMSSectionSerializer(serializers.ModelSerializer):
    """image_url mirrors ProductImageSerializer.get_image_url: CMSSection.image
    is sometimes an external URL (e.g. a hero slide sourced from Cloudinary or
    a stock-photo CDN) rather than an uploaded file, and plain ImageField
    serialization mangles those - it resolves `.url` against local/Cloudinary
    storage instead of passing an already-absolute URL straight through.
    """

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CMSSection
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        name = obj.image.name
        if name.startswith('http://') or name.startswith('https://'):
            return name
        return obj.image.url
