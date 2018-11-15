from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.serializers import AreasSerializer, SubAreasSerializer
from .models import Area

# Create your views here.

# 行政区和子行政区区分查询
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """"""
    def get_queryset(self):
        if self.action == "list":
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AreasSerializer
        else:
            return SubAreasSerializer
