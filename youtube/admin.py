from django.contrib import admin

from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

# Register your models here.

class RuleCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel')

class RuleAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'rule_collection')

admin.site.register(Rule)
admin.site.register(RuleCollection, RuleCollectionAdmin)
