from wiki.models import Fish
from rest_framework import serializers

class FishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fish
        fields = '__all__'
