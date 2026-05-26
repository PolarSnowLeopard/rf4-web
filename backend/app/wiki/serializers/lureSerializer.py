from rest_framework import serializers
from wiki.models import Lure


class LureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lure
        fields = '__all__'
