document.addEventListener('DOMContentLoaded', () => {
    /* =========================================
       1. ALERTA SI SELECCIONAN "NO ASISTIRÉ"
    ========================================= */
    const formRsvp = document.getElementById('form-rsvp');
    if (formRsvp) {
        formRsvp.addEventListener('submit', (e) => {
            const select = formRsvp.querySelector('select[name="asistira"]').value;
            if (select === 'No') {
                const confirmacion = confirm("¡Oh no! ¿Estás seguro de que te perderás la mejor Pool Party del año?");
                if (!confirmacion) {
                    e.preventDefault(); 
                }
            }
        });
    }

    /* =========================================
       2. BLOQUEO DEL FORMULARIO EL 30 DE SEPTIEMBRE
    ========================================= */
    // La fecha límite es el 30 de septiembre de 2026 a las 23:59:59
    const fechaLimite = new Date("September 30, 2026 23:59:59").getTime();
    const ahora = new Date().getTime();
    
    const mensajeCierre = document.getElementById('mensaje-cierre');

    if (ahora > fechaLimite) {
        // Si ya pasamos la fecha, ocultamos el formulario y mostramos el mensaje
        if(formRsvp) formRsvp.style.display = 'none';
        if(mensajeCierre) mensajeCierre.style.display = 'block';
    }

    /* =========================================
       3. CRONÓMETRO HASTA EL 5 DE OCTUBRE A LAS 12 AM
    ========================================= */
    // La fecha objetivo es el 5 de octubre de 2026 a las 00:00:00
    const fechaCumple = new Date("October 5, 2026 00:00:00").getTime();

    const spanDias = document.getElementById("dias");
    const spanHoras = document.getElementById("horas");
    const spanMin = document.getElementById("min");
    const spanSeg = document.getElementById("seg");

    if(spanDias) { // Verificamos que el reloj exista en la página
        const actualizarReloj = setInterval(function() {
            const tiempoActual = new Date().getTime();
            const distancia = fechaCumple - tiempoActual;

            // Cálculos de tiempo
            const dias = Math.floor(distancia / (1000 * 60 * 60 * 24));
            const horas = Math.floor((distancia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutos = Math.floor((distancia % (1000 * 60 * 60)) / (1000 * 60));
            const segundos = Math.floor((distancia % (1000 * 60)) / 1000);

            // Mostrar el resultado con ceros a la izquierda (ej: "05" en vez de "5")
            spanDias.innerHTML = dias < 10 ? "0" + dias : dias;
            spanHoras.innerHTML = horas < 10 ? "0" + horas : horas;
            spanMin.innerHTML = minutos < 10 ? "0" + minutos : minutos;
            spanSeg.innerHTML = segundos < 10 ? "0" + segundos : segundos;

            // Si se llega a la fecha
            if (distancia < 0) {
                clearInterval(actualizarReloj);
                document.querySelector('.contador-container').innerHTML = "<h3 style='color: #00ffff;'>¡Llegó el gran día! 🎉</h3>";
            }
        }, 1000); // Se actualiza cada 1 segundo (1000 ms)
    }
});