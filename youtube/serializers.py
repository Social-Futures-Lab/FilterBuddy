from rest_framework import serializers
from .models import Comment, RuleCollection
from .util_rules import pretty_date

class RuleCollectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RuleCollection
        fields = (
            'id', 'name', 'create_date'
        )

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date'
        )        

    def to_representation(self, instance):
        representation = super(CommentSerializer, self).to_representation(instance)

        representation['pub_date'] = pretty_date(instance.pub_date.isoformat())
        return representation        