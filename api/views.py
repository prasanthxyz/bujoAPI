""" Views for Api App """

from datetime import datetime
import dateutil.parser
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

    @action(methods=['GET'], detail=False)
    def get_day_entries(self, request):
        """ Get one day's entries """
        posted_day = request.GET.get('day')

        try:
            day = dateutil.parser.parse(posted_day)
        except (AttributeError, TypeError, ValueError):
            day = datetime.today()

        queryset = Entry.objects.all().filter(
            user=request.user,
            date_created__year=day.year,
            date_created__month=day.month,
            date_created__day=day.day)
        serializer = EntrySerializer(queryset, many=True)
        return Response(serializer.data)
