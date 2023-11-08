from django.contrib import admin
from ChatBot.models import *
# Register your models here.

class MessageModelAdmin(admin.ModelAdmin):
    list_display = ('user_name','phone_number','meessage', 'message_file')

admin.site.register(CustomUser)
admin.site.register(MessageModel,MessageModelAdmin)