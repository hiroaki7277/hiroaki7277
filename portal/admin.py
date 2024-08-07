from django.contrib import admin
from .models import Post, Comment, Like, Profile, Department, Position

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Profile)
admin.site.register(Department)
admin.site.register(Position)
