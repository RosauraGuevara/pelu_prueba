document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    console.log(calendarEl);
    var inputFecha = document.getElementById('fecha');
    console.log(inputFecha);
    var calendar = new FullCalendar.Calendar(calendarEl, {
    
        initialView: 'dayGridMonth',
        locale: 'es',  // Configurar el idioma a español
        selectable: true,
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch('/citas')
            .then(response => response.json())
            .then(events => {
                console.log("Eventos cargados:", events);  // Ver los eventos cargados en la consola
                successCallback(events);  // Pasar los eventos a FullCalendar
            })
            .catch(error => {
                console.error("Error cargando los eventos:", error);  // Mostrar el error si ocurre
                failureCallback(error);
            });
        
        },
        
        select: function(info) {
            var eventos = calendar.getEvents();
            console.log("Eventos al seleccionar: ", eventos);  // Asegúrate de que haya eventos cargados
            var disponible = eventos.find(event => event.startStr === info.startStr && event.title === "Disponible");
            console.log("Evento disponible: ", disponible);  // Ver si se encuentra un evento disponible
            if (disponible) {
                inputFecha.value = info.startStr;
                calendarEl.style.display = 'none';
            } else {
                alert("No hay disponibilidad en esta fecha.");
            }
        }
        
    });
    

    // Renderizar el calendario pero mantenerlo oculto
    calendar.render();
    calendarEl.style.display = 'none';
    console.log(calendar);
    console.log(calendarEl);
    // Mostrar el calendario cuando se hace clic en el input de fecha
    inputFecha.addEventListener('focus', function() {
        calendarEl.style.display = 'block';  // Mostrar el calendario
    });
    console.log(calendar.render);
    console.log(calendarEl.style.display);
    console.log(inputFecha);
    console.log(calendarEl);
    // Ocultar el calendario si se hace clic fuera de él
    document.addEventListener('click', function(event) {
        if (!calendarEl.contains(event.target) && event.target !== inputFecha) {
            calendarEl.style.display = 'none';  // Ocultar el calendario si se hace clic fuera
        }
    });
    console.log(document);
    document.getElementById('fecha').addEventListener('change', function() {
        // Código para mostrar las horas disponibles según el servicio y fecha seleccionados
    });
    
});

document.getElementById('fecha').addEventListener('change', function() {
    var fechaSeleccionada = this.value;
    var servicioSeleccionado = document.getElementById('servicio').value;
    console.log(fechaSeleccionada);
    console.log(servicioSeleccionado);
    if (fechaSeleccionada && servicioSeleccionado) {
        fetch('/get_horas_disponibles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fecha: fechaSeleccionada,
                servicio_id: servicioSeleccionado
                
            })
        })
        .then(response => response.json())
        .then(data => {
            var horaSelect = document.getElementById('hora');
            console.log(servicioSeleccionado);
            console.log(fechaSeleccionada);
            console.log(horaSelect);
            console.log(document);
            horaSelect.innerHTML = '';  // Limpiar las opciones actuales

            if (data.horas_disponibles && data.horas_disponibles.length > 0) {
                data.horas_disponibles.forEach(function(hora) {
                    var option = document.createElement('option');
                    option.value = hora;
                    option.textContent = hora;
                    horaSelect.appendChild(option);
                    console.log(data);
                    console.log(option);
                    console.log(horaSelect);
                    console.log(data.horas_disponibles);
                    console.log(hora);
                    console.log(option.textContent);
                    console.log(data.horas_disponibles.length);
                });
            } else {
                alert("No hay horas disponibles para esta fecha.");
            }
        });
    }
});


