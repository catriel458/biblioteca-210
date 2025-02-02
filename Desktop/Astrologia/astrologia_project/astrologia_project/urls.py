from django.contrib import admin
from django.urls import path
from astro.views import home, video_upload

from django.contrib import admin
from django.urls import path
from astro.views import home, video_upload, video_edit, video_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('subir-video/', video_upload, name='video_upload'),
    path('editar-video/<int:video_id>/', video_edit, name='video_edit'),
    path('borrar-video/<int:video_id>/', video_delete, name='video_delete'),
]