from rest_framework import serializers
from . import models


class AreasSerializer(serializers.ModelSerializer):
    """行政区序列化器"""
    class Meta:
        model = models.Area
        fields = ("id", "name")


class SubAreasSerializer(serializers.ModelSerializer):
    """子行政区序列化器"""
    subs = AreasSerializer(many=True, read_only=True)
    class Meta:
        model = models.Area
        fields = ("id", "name", "subs")



