from rest_framework import serializers
from wiki.models import Accessory


class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessory
        fields = '__all__'
