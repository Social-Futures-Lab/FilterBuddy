from rest_framework import serializers
from .models import Comment, Video, RuleCollection
from .util_rules import pretty_date

class RuleCollectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RuleCollection
        fields = (
            'id', 'name', 'create_date'
        )

class VideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = (
            'id', 'video_id', 'title'
        )        


    def to_representation(self, instance):
        representation = super(VideoSerializer, self).to_representation(instance)
        representation['title'] = (instance.video_id, instance.title)
        return representation         
           

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    video = VideoSerializer()

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date', 'video'
        )        

    def to_representation(self, instance):
        representation = super(CommentSerializer, self).to_representation(instance)
        representation['pub_date'] = pretty_date(instance.pub_date.isoformat())
        return representation        