from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import CMSSection
from .serializers import CMSSectionSerializer


class CMSSectionImageUrlTests(TestCase):
    # Regression guard: CMSSection.image is sometimes a real external URL
    # (a hero slide sourced from Cloudinary or a stock-photo CDN) rather than
    # an uploaded file. Serializing it through the plain ImageField used to
    # mangle it via local/Cloudinary storage's .url() instead of passing the
    # already-absolute URL straight through - see get_image_url on
    # ProductImageSerializer, which this mirrors.
    def test_external_url_is_passed_through_unchanged(self):
        section = CMSSection.objects.create(
            title='New Season',
            slug='hero-new-season',
            section_type=CMSSection.SectionType.HERO,
            image='https://picsum.photos/seed/oghie-hero-tailoring/1600/900',
        )

        data = CMSSectionSerializer(section).data

        self.assertEqual(
            data['image_url'], 'https://picsum.photos/seed/oghie-hero-tailoring/1600/900',
        )

    def test_blank_image_serializes_to_none(self):
        section = CMSSection.objects.create(
            title='No Image', slug='no-image', section_type=CMSSection.SectionType.CONTENT,
        )

        data = CMSSectionSerializer(section).data

        self.assertIsNone(data['image_url'])

    def test_uploaded_file_resolves_through_storage_url(self):
        section = CMSSection.objects.create(
            title='Uploaded',
            slug='uploaded-image',
            section_type=CMSSection.SectionType.HERO,
            image=SimpleUploadedFile('hero.jpg', b'fake-image-bytes', content_type='image/jpeg'),
        )

        data = CMSSectionSerializer(section).data

        self.assertEqual(data['image_url'], section.image.url)
        self.assertFalse(data['image_url'].startswith('http'))
