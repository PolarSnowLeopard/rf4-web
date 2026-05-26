from rest_framework import serializers
from wiki.models import Hook


class HookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hook
        fields = '__all__'
