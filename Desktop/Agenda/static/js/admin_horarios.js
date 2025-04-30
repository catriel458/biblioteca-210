// Función global para cargar horarios
function cargarHorarios() {
    const listaHorarios = document.getElementById('horarios-lista');
    if (!listaHorarios) return;

    listaHorarios.innerHTML = '<tr><td colspan="3" class="text-center"><div class="spinner-border text-primary" role="status"></div></td></tr>';
    
    fetch('/admin/horarios/get_horarios/')
        .then(response => response.json())
        .then(data => {
            listaHorarios.innerHTML = '';
            if (data.length === 0) {
                listaHorarios.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center py-4">
                            <i class="fas fa-clock fa-2x text-muted mb-3"></i>
                            <p class="mb-0">No hay horarios configurados</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            data.forEach(horario => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>
                        <div class="d-flex align-items-center">
                            <i class="fas fa-clock text-primary me-2"></i>
                            ${horario.hora_inicio}
                        </div>
                    </td>
                    <td>
                        <span class="badge rounded-pill bg-${horario.disponible ? 'success' : 'danger'}">
                            <i class="fas fa-${horario.disponible ? 'check' : 'times'} me-1"></i>
                            ${horario.disponible ? 'Disponible' : 'No disponible'}
                        </span>
                    </td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline-danger eliminar-horario" data-id="${horario.id}">
                            <i class="fas fa-trash me-1"></i>Eliminar
                        </button>
                    </td>
                `;
                listaHorarios.appendChild(row);
            });

            // Actualizar los event listeners de los botones de eliminar
            document.querySelectorAll('.eliminar-horario').forEach(btn => {
                btn.addEventListener('click', eliminarHorarioHandler);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los horarios'
            });
        });
}

// Función para manejar la eliminación de horarios
function eliminarHorarioHandler() {
    const horarioId = this.dataset.id;
    if (!horarioId) return;

    Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/admin/horarios/${horarioId}/eliminar/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    mostrarMensaje('success', 'Horario eliminado correctamente');
                    cargarHorarios(); // Recargar la lista después de eliminar
                } else {
                    mostrarMensaje('error', data.message || 'Error al eliminar el horario');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('error', 'Error al procesar la solicitud');
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Cargar horarios al iniciar la página
    cargarHorarios();

    // Inicializar Flatpickr para el selector de fecha
    if (document.querySelector('input[name="fecha"]')) {
        flatpickr('input[name="fecha"]', {
            locale: 'es',
            dateFormat: 'Y-m-d',
            minDate: 'today'
        });
    }

    // Función para mostrar mensajes
    function mostrarMensaje(tipo, mensaje) {
        Swal.fire({
            icon: tipo,
            title: tipo === 'success' ? 'Éxito' : 'Error',
            text: mensaje,
            timer: tipo === 'success' ? 1500 : undefined,
            showConfirmButton: tipo !== 'success'
        });
    }

    // Función para obtener el token CSRF
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Guardar nuevo horario
    const btnGuardarHorario = document.getElementById('guardarHorario');
    if (btnGuardarHorario) {
        btnGuardarHorario.addEventListener('click', function() {
            const formHorario = document.getElementById('formHorario');
            const formData = new FormData(formHorario);

            const formDataObj = Object.fromEntries(formData);
            const horarioData = {
                dia_semana: 0, // Por defecto Lunes
                hora_inicio: formDataObj.hora_inicio,
                hora_fin: formDataObj.hora_inicio, // Mismo valor que hora_inicio
                duracion_turno: 30 // Duración por defecto en minutos
            };

            fetch('/admin/horarios/configurar/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(horarioData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    mostrarMensaje('success', 'Horario guardado correctamente');
                    const modalHorario = bootstrap.Modal.getInstance(document.getElementById('modalHorario'));
                    modalHorario.hide();
                    cargarHorarios(); // Usar la función de cargar horarios en lugar de recargar la página
                } else {
                    mostrarMensaje('error', data.message || 'Error al guardar el horario');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('error', 'Error al procesar la solicitud');
            });
        });
    }

    // Guardar excepción
    const btnGuardarExcepcion = document.getElementById('guardarExcepcion');
    if (btnGuardarExcepcion) {
        btnGuardarExcepcion.addEventListener('click', function() {
            const formExcepcion = document.getElementById('formExcepcion');
            const formData = new FormData(formExcepcion);
            const data = Object.fromEntries(formData);
            data.disponible = formExcepcion.querySelector('[name="disponible"]').checked;

            fetch('/admin/horarios/excepcion/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    mostrarMensaje('success', 'Excepción guardada correctamente');
                    const modalExcepcion = bootstrap.Modal.getInstance(document.getElementById('modalExcepcion'));
                    modalExcepcion.hide();
                    location.reload(); // Recargar para mostrar los cambios
                } else {
                    mostrarMensaje('error', data.message || 'Error al guardar la excepción');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('error', 'Error al procesar la solicitud');
            });
        });
    }

    // Eliminar horario
    document.querySelectorAll('.eliminar-horario').forEach(btn => {
        btn.addEventListener('click', function() {
            const horarioId = this.closest('tr').dataset.id;
            if (!horarioId) return;

            Swal.fire({
                title: '¿Estás seguro?',
                text: 'Esta acción no se puede deshacer',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/admin/horarios/${horarioId}/eliminar/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCSRFToken()
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            mostrarMensaje('success', 'Horario eliminado correctamente');
                            this.closest('tr').remove();
                        } else {
                            mostrarMensaje('error', data.message || 'Error al eliminar el horario');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        mostrarMensaje('error', 'Error al procesar la solicitud');
                    });
                }
            });
        });
    });
});