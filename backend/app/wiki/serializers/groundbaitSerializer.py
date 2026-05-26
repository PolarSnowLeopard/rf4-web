from rest_framework import serializers
from wiki.models import Groundbait


class GroundbaitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groundbait
        fields = '__all__'
