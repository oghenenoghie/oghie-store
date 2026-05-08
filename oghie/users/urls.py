from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, UserProfileViewSet

app_name = 'users'

router = DefaultRouter()
router.register('profiles', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current-user'),
] + router.urls
