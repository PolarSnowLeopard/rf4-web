from rest_framework import serializers
from wiki.models import Bait


class BaitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bait
        fields = '__all__'
