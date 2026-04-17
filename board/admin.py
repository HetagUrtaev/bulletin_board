from django.contrib import admin
from .models import Category, Ad, Response, UserProfile


admin.site.register(Category)
admin.site.register(Ad)
admin.site.register(Response)
admin.site.register(UserProfile)
