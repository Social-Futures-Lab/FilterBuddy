from rest_framework import serializers
from .models import RuleCollection

class RuleCollectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RuleCollection
        fields = (
            'id', 'name', 'create_date'
        )