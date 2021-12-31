from django.contrib import admin
from .models import *


admin.site.register(Account)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(ChatRoomName)
admin.site.register(Message)