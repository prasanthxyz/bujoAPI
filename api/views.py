# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics
from serializers import EntrySerializer
from models import Entry
from rest_framework.permissions import IsAuthenticated


class CreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save(user=self.request.user)
