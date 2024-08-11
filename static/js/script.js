document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var inputFecha = document.getElementById('fecha');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: '/citas',  // Fetch existing events from the server
        select: function(info) {
            inputFecha.value = info.startStr;  // Update the input with the selected date
            calendarEl.style.display = 'none';  // Hide the calendar
        }
    });

    inputFecha.addEventListener('focus', function() {
        calendarEl.style.display = 'block';  // Show the calendar when the input is focused
    });

    document.addEventListener('click', function(event) {
        if (!calendarEl.contains(event.target) && event.target !== inputFecha) {
            calendarEl.style.display = 'none';  // Hide the calendar if clicking outside
        }
    });

    calendar.render();
});

document.getElementById('pago').addEventListener('change', function() {
    var display = this.value == 'Transferencia' ? 'block' : 'none';
    document.getElementById('transferencia-info').style.display = display;
});