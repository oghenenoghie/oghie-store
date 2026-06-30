from rest_framework.routers import DefaultRouter

from .views import CMSSectionViewSet

app_name = 'cms'

router = DefaultRouter()
router.register('sections', CMSSectionViewSet, basename='cms-section')

urlpatterns = router.urls
