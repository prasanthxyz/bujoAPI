# -*- coding: utf-8 -*-
from rest_framework import viewsets
from serializers import EntrySerializer
from models import Entry
from rest_framework.permissions import IsAuthenticated


class EntryViewSet(viewsets.ModelViewSet):
    """ Entry model viewset """
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Add user to entry while saving."""
        serializer.save(user=self.request.user)
