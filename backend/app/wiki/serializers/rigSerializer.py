from rest_framework import serializers
from wiki.models import Rig


class RigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rig
        fields = '__all__'
