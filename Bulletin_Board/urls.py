from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from board.views import Profile
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache
from django.conf import settings

from ckeditor_uploader.views import upload, browse

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')), # думаю можно убрать
    path('accounts/', include('allauth.urls')),
    path('profile/', Profile.as_view(), name='profile'),
    path('', include('board.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^upload/', login_required(upload), name='ckeditor_upload'),
    re_path(r'^browse/', login_required(never_cache(browse)), name='ckeditor_browse'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
