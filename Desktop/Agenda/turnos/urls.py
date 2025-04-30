from django.urls import path
from . import views
from . import admin_views
from . import historial_views  # Añadido import faltante

urlpatterns = [
    # Rutas principales
    path('', views.inicio, name='inicio'),
    path('contacto/', views.contacto, name='contacto'),
    path('solicitar-turno/', views.solicitar_turno, name='solicitar_turno'),
    path('calendario/', views.calendario, name='calendario'),
    path('dias-disponibles/', views.dias_disponibles, name='dias_disponibles'),    
    path('horarios-disponibles/<str:fecha>/', views.horarios_disponibles, name='horarios_disponibles'),
    path('confirmar-turno/', views.confirmar_turno, name='confirmar_turno'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('cancelar-turno/<int:turno_id>/', views.cancelar_turno, name='cancelar_turno'),
    
    # Rutas administrativas
    path('admin/dias-disponibles/', admin_views.dias_disponibles, name='admin_dias_disponibles'),
    path('admin/configurar-dias/', views.admin_configurar_dias, name='admin_configurar_dias'),
    path('admin/solicitar-turno/', views.admin_solicitar_turno, name='admin_solicitar_turno'),
    path('admin/confirmar-turno/', views.admin_confirmar_turno, name='admin_confirmar_turno'),
    path('admin/horarios/configurar/', admin_views.configurar_horarios, name='admin_configurar_horarios'),
    path('admin/horarios/excepcion/', admin_views.agregar_excepcion, name='admin_agregar_excepcion'),
    path('admin/horarios/<int:horario_id>/eliminar/', admin_views.eliminar_horario, name='admin_eliminar_horario'),
    path('admin/crear-disponibilidad/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('admin/usuarios/', admin_views.usuarios, name='admin_usuarios'),
    path('admin/listado-turnos/', admin_views.listado_turnos, name='admin_listado_turnos'),
    path('admin/historial-pacientes/', views.historial_paciente_lista, name='historial_paciente_lista'),
    path('admin/historial-pacientes/<int:paciente_id>/', views.historial_paciente_ver, name='historial_paciente_ver'),
    path('admin/historial-pacientes/<int:paciente_id>/pdf/', views.historial_paciente_pdf, name='historial_paciente_pdf'),
    path('admin/historial-pacientes/<int:paciente_id>/no-disponible/', views.historial_paciente_nodisponible, name='historial_paciente_nodisponible'),
    
    # URLs para la gestión del historial de pacientes
    path('admin/historial/<int:paciente_id>/', historial_views.admin_historial_paciente, name='admin_historial_paciente'),
    path('admin/historial/<int:paciente_id>/get_historial/', historial_views.get_historial, name='get_historial'),
    path('admin/historial/crear/', historial_views.crear_registro, name='crear_historial'),
    path('admin/historial/<int:registro_id>/obtener/', historial_views.obtener_registro, name='obtener_registro'),
    path('admin/historial/<int:registro_id>/actualizar/', historial_views.actualizar_registro, name='actualizar_registro'),
    path('admin/historial/<int:registro_id>/eliminar/', historial_views.eliminar_registro, name='eliminar_registro'),
]