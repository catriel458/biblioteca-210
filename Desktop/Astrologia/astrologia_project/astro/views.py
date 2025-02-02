from django.shortcuts import render, redirect, get_object_or_404
from .models import Video
from django.contrib.auth.models import User
from .forms import VideoForm

def home(request):
    videos = Video.objects.all().order_by('-fecha_publicacion')
    return render(request, 'home.html', {'videos': videos})

def video_upload(request):
    # Asegurarse de que existe un usuario
    if not User.objects.exists():
        User.objects.create_user('admin', 'admin@example.com', 'admin123')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        url_youtube = request.POST.get('url_youtube')
        
        # Crear el video
        Video.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            url_youtube=url_youtube,
            autor=User.objects.first()
        )
        return redirect('home')
    
    return render(request, 'video_upload.html')

def video_edit(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = VideoForm(instance=video)
    
    return render(request, 'video_edit.html', {'form': form, 'video': video})

def video_delete(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        video.delete()
        return redirect('home')
    
    return render(request, 'video_delete.html', {'video': video})