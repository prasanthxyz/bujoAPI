""" Views for Api App """

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.serializers import EntrySerializer
from api.models import Entry


class EntryViewSet(viewsets.ModelViewSet):
    """ Entry model viewset """
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Add user to entry while saving."""
        serializer.save(user=self.request.user)
