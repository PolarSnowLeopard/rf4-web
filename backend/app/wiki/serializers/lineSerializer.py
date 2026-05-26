from rest_framework import serializers
from wiki.models import Line


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = '__all__'
