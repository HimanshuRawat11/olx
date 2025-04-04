from django.contrib import admin
from .models import Chat, Message , GroupAdmin
# Register your models here.

admin.site.register(Chat, )
admin.site.register(GroupAdmin, )
admin.site.register(Message, )
