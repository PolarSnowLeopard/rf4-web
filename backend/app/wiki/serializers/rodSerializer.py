from rest_framework import serializers
from wiki.models import Rod


class RodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rod
        fields = '__all__'
