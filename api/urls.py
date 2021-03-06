""" Entry Urls module """

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from api.views import EntryViewSet

router = DefaultRouter()
router.register(r'entries', EntryViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
