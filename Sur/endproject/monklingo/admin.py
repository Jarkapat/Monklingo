from django.contrib import admin
from .models import ChatRoom, Message, Route, Checkpoint

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Route)
admin.site.register(Checkpoint)