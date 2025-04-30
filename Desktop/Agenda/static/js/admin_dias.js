document.addEventListener('DOMContentLoaded', function() {
    const formAgregarDia = document.getElementById('formAgregarDia');
    const fechaInput = document.getElementById('fecha');
    
    // Establecer fecha mínima como hoy
    const hoy = new Date();
    fechaInput.min = hoy.toISOString().split('T')[0];
    
    formAgregarDia.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('fecha', fechaInput.value);
        formData.append('disponible', document.getElementById('disponible').checked);
        
        fetch('/turnos/admin/configurar-dias/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: 'El día se ha configurado correctamente',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    formAgregarDia.reset();
                    cargarDiasDisponibles();
                });
            } else {
                throw new Error(data.message || 'Error al configurar el día');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error al configurar el día'
            });
        });
    });

    // Función para cargar los días disponibles
    function cargarDiasDisponibles() {
        fetch('/turnos/admin/dias-disponibles/')
            .then(response => response.json())
            .then(data => {
                const tablaDias = document.getElementById('dias-lista') || document.createElement('tbody');
                tablaDias.id = 'dias-lista';
                tablaDias.innerHTML = '';
                
                data.forEach(dia => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${dia.fecha}</td>
                        <td>
                            <span class="badge bg-${dia.disponible ? 'success' : 'danger'}">
                                ${dia.disponible ? 'Disponible' : 'No disponible'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info ver-horarios" data-fecha="${dia.fecha}">
                                <i class="fas fa-clock me-1"></i>Ver horarios
                            </button>
                        </td>
                    `;
                    tablaDias.appendChild(tr);
                });
                
                // Si la tabla no está en el DOM, agregarla
                const tablaExistente = document.getElementById('dias-lista');
                if (!tablaExistente) {
                    document.querySelector('.table tbody').replaceWith(tablaDias);
                }
            })
            .catch(error => {
                console.error('Error al cargar días:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los días disponibles'
                });
            });
    }

    // Cargar días disponibles al iniciar
    cargarDiasDisponibles();

    // Agregar manejador de eventos para los botones de ver horarios
    document.addEventListener('click', function(e) {
        if (e.target.closest('.ver-horarios')) {
            const fecha = e.target.closest('.ver-horarios').dataset.fecha;
            mostrarHorarios(fecha);
        }
    });

    function mostrarHorarios(fecha) {
        fetch(`/turnos/admin/horarios-dia/${fecha}/`)
            .then(response => response.json())
            .then(data => {
                let horariosHTML = '';
                if (data.horarios && data.horarios.length > 0) {
                    horariosHTML = data.horarios.map(horario => `
                        <div class="mb-2">
                            <span class="badge bg-${horario.disponible ? 'success' : 'danger'}">
                                ${horario.hora} - ${horario.disponible ? 'Disponible' : 'No disponible'}
                            </span>
                        </div>
                    `).join('');
                } else {
                    horariosHTML = '<p class="text-muted">No hay horarios configurados para este día</p>';
                }

                Swal.fire({
                    title: `Horarios para ${fecha}`,
                    html: horariosHTML,
                    confirmButtonText: 'Cerrar'
                });
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los horarios'
                });
            });
    }
});