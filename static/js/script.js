document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var inputFecha = document.getElementById('fecha');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',  // Configurar el idioma a español
        selectable: true,
        events: '/citas',  // Cargar eventos desde el servidor
        select: function(info) {
            var eventos = calendar.getEvents();
            var disponible = eventos.find(event => event.startStr === info.startStr && event.title === "Disponible");

            if (disponible) {
                inputFecha.value = info.startStr;  // Actualizar el input con la fecha seleccionada
                calendarEl.style.display = 'none';  // Ocultar el calendario después de seleccionar
            } else {
                alert("No hay disponibilidad en esta fecha.");
            }
        }
    });

    // Renderizar el calendario pero mantenerlo oculto
    calendar.render();
    calendarEl.style.display = 'none';

    // Mostrar el calendario cuando se hace clic en el input de fecha
    inputFecha.addEventListener('focus', function() {
        calendarEl.style.display = 'block';  // Mostrar el calendario
    });

    // Ocultar el calendario si se hace clic fuera de él
    document.addEventListener('click', function(event) {
        if (!calendarEl.contains(event.target) && event.target !== inputFecha) {
            calendarEl.style.display = 'none';  // Ocultar el calendario si se hace clic fuera
        }
    });

    document.getElementById('fecha').addEventListener('change', function() {
        // Código para mostrar las horas disponibles según el servicio y fecha seleccionados
    });
    
});
