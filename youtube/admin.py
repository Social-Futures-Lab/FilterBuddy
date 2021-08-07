from django.contrib import admin

from .models import Channel, RuleCollection, RuleColTemplate, Rule, Video, Comment

# Register your models here.

class ChannelAdmin(admin.ModelAdmin):
  list_display = ('title', 'description', 'pub_date', 'channel_id')

class RuleInline(admin.TabularInline):
    model = Rule    

class RuleCollectionAdmin(admin.ModelAdmin):
  list_display = ('name', 'owner', 'id', 'rules')
  inlines = [RuleInline, ]

  def rules(self, obj):
    return ", ".join([rule.phrase for rule in obj.rule_set.all()])  

class RuleColTemplateAdmin(admin.ModelAdmin):
  list_display = ('name', 'id', 'rules', 'description', 'num_users')  
  inlines = [RuleInline, ]

  def rules(self, obj):
    return ", ".join([rule.phrase for rule in obj.rule_set.all()])    

class RuleAdmin(admin.ModelAdmin):
  list_display = ('phrase', 'rule_collection', 'id')

class VideoAdmin(admin.ModelAdmin):
  list_display = ('title', 'pub_date', 'channel', 'video_id')

class CommentAdmin(admin.ModelAdmin):
  list_display = ('text', 'video', 'pub_date', 'author', 'likeCount', 'comment_id', 'parent_id')

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleCollection, RuleCollectionAdmin)
admin.site.register(RuleColTemplate, RuleColTemplateAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)