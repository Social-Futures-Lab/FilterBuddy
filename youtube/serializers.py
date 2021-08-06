from rest_framework import serializers
from .models import Comment, Video, RuleCollection
from .util_rules import pretty_date, getCatchingCollection, getChannel

class RuleCollectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RuleCollection
        fields = (
            'id', 'name', 'create_date'
        )

class VideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url_id_and_title = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = (
            'id', 'video_id', 'title', 'url_id_and_title',
        )        


    def to_representation(self, instance):
        representation = super(VideoSerializer, self).to_representation(instance)
        representation['url_id_and_title'] = (instance.video_id, instance.title)
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

class AllCommentsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    video = VideoSerializer()
    caught_by_collection = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date', 'video', 'caught_by_collection'
        )        

    def to_representation(self, instance):
        myChannel = getChannel(self.context['request'])
        myCollections = RuleCollection.objects.filter(owner = myChannel)

        representation = super(AllCommentsSerializer, self).to_representation(instance)
        representation['pub_date'] = pretty_date(instance.pub_date.isoformat())
        representation['caught_by_collection'] = getCatchingCollection(instance, myCollections)
        return representation                