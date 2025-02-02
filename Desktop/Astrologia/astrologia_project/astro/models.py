from django.db import models
from django.contrib.auth.models import User
import re

class Video(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    url_youtube = models.URLField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_youtube_id(self):
        # Patrones para URLs de YouTube
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

        match = re.match(youtube_regex, self.url_youtube)
        if match:
            return match.group(6)
        return None

    def __str__(self):
        return self.titulo