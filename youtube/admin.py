from django.contrib import admin

from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

# Register your models here.

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'pub_date', 'channel_id')

class RuleCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'id', 'is_template')

class RuleAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'rule_collection', 'id')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'channel', 'video_id')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'video', 'pub_date', 'author', 'likeCount', 'comment_id')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'likeCount', 'comment', 'reply_id')

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleCollection, RuleCollectionAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
