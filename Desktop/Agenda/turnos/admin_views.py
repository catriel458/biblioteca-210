# turnos/admin_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import DiasDisponibles, HorarioDisponible, Turno
from .horarios_config import ConfiguracionHorario, ExcepcionHorario
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, time

def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.rol == 'admin')

@login_required
def usuarios(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener lista de usuarios
    usuarios = User.objects.all().order_by('-date_joined')
    
    return render(request, 'admin/usuarios.html', {
        'title': 'Gestión de Usuarios',
        'usuarios': usuarios
    })

@user_passes_test(es_admin)
def configurar_horarios(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            horario = ConfiguracionHorario.objects.create(
                dia_semana=int(data['dia_semana']),
                hora_inicio=data['hora_inicio'],
                hora_fin=data['hora_fin'],
                duracion_turno=int(data['duracion_turno'])
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Horario configurado correctamente',
                'id': horario.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    configuraciones = ConfiguracionHorario.objects.filter(activo=True).order_by('dia_semana', 'hora_inicio')
    excepciones = ExcepcionHorario.objects.all().order_by('fecha')
    
    return render(request, 'admin/configurar_horarios.html', {
        'configuraciones': configuraciones,
        'excepciones': excepciones
    })

@user_passes_test(es_admin)
def get_horarios(request):
    horarios = HorarioDisponible.objects.values('id', 'hora_inicio', 'disponible').distinct()
    return JsonResponse(list(horarios), safe=False)

@user_passes_test(es_admin)
@require_http_methods(['POST', 'DELETE'])
def eliminar_horario(request, horario_id):
    # Manejar solicitudes DELETE para ConfiguracionHorario
    if request.method == 'DELETE':
        try:
            horario = ConfiguracionHorario.objects.get(id=horario_id)
            horario.delete()
            return JsonResponse({'status': 'success', 'message': 'Horario eliminado correctamente'})
        except ConfiguracionHorario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Horario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # Manejar solicitudes POST para HorarioDisponible
    try:
        horario = HorarioDisponible.objects.get(id=horario_id)
        horario.delete()
        return JsonResponse({'success': True})
    except HorarioDisponible.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@user_passes_test(es_admin)
def dias_disponibles(request):
    if request.method == 'POST':
        try:
            fecha = request.POST.get('fecha')
            disponible = request.POST.get('disponible') == 'true'
            
            dia, created = DiasDisponibles.objects.update_or_create(
                fecha=fecha,
                defaults={'disponible': disponible}
            )
            
            # Si el día es creado o actualizado como disponible
            if disponible:
                # Comprobar si es un día recién creado
                if created:
                    # Obtener horarios base existentes o usar predeterminados
                    horarios_base = list(HorarioDisponible.objects.values_list('hora_inicio', flat=True).distinct())
                    if not horarios_base:
                        # Horarios predeterminados si no hay existentes
                        horarios_base = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                                        '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                        
                    for hora in horarios_base:
                        HorarioDisponible.objects.create(
                            dia=dia,
                            hora_inicio=hora,
                            disponible=True
                        )
                else:
                    # Si no es un día nuevo, usar horarios predeterminados
                    horarios = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                               '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                    
                    for hora in horarios:
                        HorarioDisponible.objects.get_or_create(
                            dia=dia,
                            hora_inicio=hora,
                            defaults={'disponible': True}
                        )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Día configurado correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # GET request - retornar lista de días disponibles
    dias = DiasDisponibles.objects.all().order_by('fecha')
    dias_list = [{
        'id': dia.id,
        'fecha': dia.fecha.strftime('%Y-%m-%d'),
        'disponible': dia.disponible
    } for dia in dias]
    
    return JsonResponse(dias_list, safe=False)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def agregar_excepcion(request):
    try:
        data = json.loads(request.body)
        fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        disponible = data.get('disponible', False)
        motivo = data.get('motivo', '')

        excepcion, created = ExcepcionHorario.objects.update_or_create(
            fecha=fecha,
            defaults={
                'disponible': disponible,
                'motivo': motivo
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Excepción agregada correctamente'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def listado_turnos(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    estado = request.GET.get('estado')
    
    # Consulta base
    turnos = Turno.objects.all()
    
    # Aplicar filtros si existen
    if fecha_desde:
        turnos = turnos.filter(dia__fecha__gte=fecha_desde)
    
    if fecha_hasta:
        turnos = turnos.filter(dia__fecha__lte=fecha_hasta)
        
    if estado:
        turnos = turnos.filter(estado=estado)
        
    # Ordenar por fecha y hora
    turnos = turnos.order_by('dia__fecha', 'horario__hora_inicio')
    
    # Contexto para la plantilla
    context = {
        'title': 'Listado de Turnos',
        'turnos': turnos,
        'filtros': {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'estado': estado
        }
    }
    
    return render(request, 'admin/listado_turnos.html', context)