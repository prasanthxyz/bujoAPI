"""Entry Urls module"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import EntryViewSet

router = DefaultRouter()
router.register(r"entries", EntryViewSet)

urlpatterns = [path("", include(router.urls))]
