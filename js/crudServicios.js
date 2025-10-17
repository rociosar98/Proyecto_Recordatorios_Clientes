document.addEventListener("DOMContentLoaded", async () => {
    const token = sessionStorage.getItem("token");
    const usuario = JSON.parse(sessionStorage.getItem("usuario")); //Recupera del sessionStorage el token de autenticación y el usuario logueado (parseado como objeto JS).
    const saludo = document.getElementById("adminSaludo");
    const tabla = document.getElementById("serviciosTabla");
    const form = document.getElementById("crudForm");

    const btnCrear = document.getElementById("btnCrear");
    const btnActualizar = document.getElementById("btnActualizar");
    const btnEliminar = document.getElementById("btnEliminar");

    const tipoServicio = document.getElementById("tipo");
    const recurrencia = document.getElementById("recurrencia");
    const cuotas = document.getElementById("cuotas");

    let servicioSeleccionadoId = null; //Guarda el ID del destino seleccionado para editar o eliminar. Está vacío al inicio.

    if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
    } //Si hay usuario cargado en sesión, muestra un saludo personalizado en la página.

    // Lógica para habilitar/deshabilitar campos según tipo de servicio
    tipoServicio.addEventListener("change", function () {
        if (tipoServicio.value === "recurrente") {
            recurrencia.disabled = false;
            recurrencia.required = true;

            cuotas.disabled = true;
            cuotas.required = false;
            cuotas.value = "";
        } else if (tipoServicio.value === "pago_unico") {
            cuotas.disabled = false;
            cuotas.required = true;

            recurrencia.disabled = true;
            recurrencia.required = false;
            recurrencia.value = "";
        } else {
            recurrencia.disabled = true;
            cuotas.disabled = true;

            recurrencia.required = false;
            cuotas.required = false;

            recurrencia.value = "";
            cuotas.value = "";
        }
    });

    async function cargarServicios() {
    try {
        const res = await fetch("http://localhost:8000/servicios", {
        headers: { Authorization: `Bearer ${token}` }
        }); //Se le envía al servidor el token de autenticación en el header Authorization, con el formato Bearer <token>.

        if (!res.ok) throw new Error("No se pudieron obtener los servicios");

        const data = await res.json(); //Convierte la respuesta del servidor en un objeto JavaScript.
        tabla.innerHTML = "";
        data.forEach(s => {
        tabla.innerHTML += ` 
            <tr data-id="${s.id}">
            <td>${s.nombre}</td>
            <td>${s.precio}</td>
            <td>${s.tipo}</td>
            <td>${s.recurrencia}</td>
            <td>${s.cuotas}</td>
            </tr>`; //Por cada destino, agrega una nueva fila (<tr>) a la tabla HTML
            // ¿Por qué += y no solo =? Porque ya limpiaste antes la tabla con tabla.innerHTML = "", y ahora estás sumando una fila por cada destino, una tras otra.
            // Recorre cada destino (d) y crea una fila en la tabla con sus datos. Usa data-id para guardar el ID del destino.
        }); 

        document.querySelectorAll("#serviciosTabla tr").forEach(row => { //Después de llenar la tabla, esta línea selecciona todas las filas (<tr>) que estén dentro del elemento con id destinosTabla, y las recorre una por una.
        row.addEventListener("click", () => { //A cada fila le agrega un evento click. O sea, cuando el usuario hace clic en una fila de la tabla, se ejecuta la función de abajo
            const id = row.getAttribute("data-id"); //Toma el atributo data-id que habías puesto antes en la fila (con el id del destino) y lo guarda en una variable.
            seleccionarServicio(id);
        });
        });

    } catch (err) {
        alert("Error: " + err.message);
    } // Agrega un evento click a cada fila para que, al hacer clic, se llame a seleccionarDestino(id) con el ID correspondiente.
    } 

    await cargarServicios();

    async function seleccionarServicio(id) {
    try {
        const res = await fetch(`http://localhost:8000/servicios/${id}`, {
        headers: { Authorization: `Bearer ${token}` } //Se le pasa un header de autorización: Esto es para validar que el usuario tenga permiso para acceder.
        });

        if (!res.ok) throw new Error("Servicio no encontrado");

        const servicio = await res.json(); // Convierte la respuesta de la API en un objeto JS.
        // Hace fetch al backend para obtener un destino por su ID. Si no lo encuentra, lanza un error.

        document.getElementById("nombre").value = servicio.nombre;
        document.getElementById("precio").value = servicio.precio;
        document.getElementById("tipo").value = servicio.tipo;
        document.getElementById("recurrencia").value = servicio.recurrencia;
        document.getElementById("cuotas").value = servicio.cuotas;
        // Rellena los campos del formulario HTML con los datos del destino seleccionado, para que el usuario pueda editarlos.

        tipoServicio.dispatchEvent(new Event("change")); // ⚠️ Dispara el cambio para activar/desactivar campos

        servicioSeleccionadoId = id; //Guarda el id del destino en una variable global.

        btnCrear.style.display = "none";
        btnActualizar.style.display = "inline";
        btnEliminar.style.display = "inline";

    } catch (err) {
        alert("Error: " + err.message);
    }
    }
    // Crea un nuevo destino (cuando el formulario se envía)
    form.addEventListener("submit", async (e) => {
    e.preventDefault(); //Evita que el formulario haga su comportamiento por defecto (recargar la página o enviar datos de forma tradicional).
    // Al enviar el formulario, previene el comportamiento por defecto y se asegura de que no haya un destino seleccionado (porque en ese caso se actualizaría, no se crearía uno nuevo).

    if (servicioSeleccionadoId) return; //Si destinoSeleccionadoId tiene un valor, significa que estamos en modo edición y no deberíamos crear un destino nuevo. En ese caso, sale de la función y no hace nada.
    // Si estamos creando un nuevo destino, destinoSeleccionadoId estará en null, y entonces sí seguimos.

    const nuevoServicio = {
        nombre: document.getElementById("nombre").value,
        precio: document.getElementById("precio").value,
        tipo: document.getElementById("tipo").value,
        recurrencia: document.getElementById("recurrencia").value,
        cuotas: document.getElementById("cuotas").value,
        activo: true
    }; // Crea un objeto con los datos del nuevo destino, tomados desde los inputs del formulario HTML.

    try {
        const res = await fetch("http://localhost:8000/servicios", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}` //Se pasan los headers necesarios: tipo de contenido y token de autenticación.
        },
        body: JSON.stringify(nuevoServicio) // Se convierte el objeto JS (nuevoDestino) a texto JSON con JSON.stringify().
        }); 

        if (!res.ok) throw new Error("Error al crear servicio");

        alert("Servicio creado correctamente");
        form.reset();
        await cargarServicios();
    } catch (err) {
        alert("Error: " + err.message);
    } // Envía los datos al backend para crear el nuevo destino. Si todo sale bien, muestra mensaje, limpia el form y recarga la tabla.
    });

    btnActualizar.addEventListener("click", async () => {
    if (!servicioSeleccionadoId) return; //Si no hay destino seleccionado, se sale de la funcion

    const servicioActualizado = {
        nombre: document.getElementById("nombre").value,
        precio: document.getElementById("precio").value,
        tipo: document.getElementById("tipo").value,

        recurrencia: recurrencia.disabled ? null : document.getElementById("recurrencia").value || null,
        cuotas: cuotas.disabled ? null : parseInt(document.getElementById("cuotas").value) || null,

        activo: true
    }; //Se toma la información actual del formulario y se construye un objeto con los datos nuevos o modificados del destino.

    console.log("Payload de actualización:", servicioActualizado);

    try {
        const res = await fetch(`http://localhost:8000/servicios/${servicioSeleccionadoId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}` //Incluye el token de autenticación en los headers.
        },
        body: JSON.stringify(servicioActualizado) //Envía los datos actualizados en el cuerpo (body) en formato JSON.
        });

        const respBody = await res.json();
        console.log("Respuesta actualización:", res.status, respBody);

        if (!res.ok) {
          throw new Error(`Error al actualizar: ${respBody.detail ?? JSON.stringify(respBody)}`);
        }

        //if (!res.ok) throw new Error("Error al actualizar");

        alert("Servicio actualizado correctamente");
        limpiarFormulario();
        await cargarServicios();
    } catch (err) {
        alert("Error: " + err.message);
    } //Envía una petición PUT para actualizar el destino. Si todo sale bien, muestra mensaje, limpia el formulario y actualiza la tabla.
    });

    btnEliminar.addEventListener("click", async () => {
    if (!servicioSeleccionadoId) return;

    if (!confirm("¿Estás seguro de eliminar este servicio?")) return; //Si no hay destino seleccionado o el usuario no confirma, no hace nada.

    try {
        const res = await fetch(`http://localhost:8000/servicios/${servicioSeleccionadoId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Error al eliminar");

        alert("Servicio eliminado");
        limpiarFormulario();
        await cargarServicios();
    } catch (err) {
        alert("Error: " + err.message);
    }
    });


    function limpiarFormulario() {
    form.reset();
    servicioSeleccionadoId = null;
    btnCrear.style.display = "inline";
    btnActualizar.style.display = "none";
    btnEliminar.style.display = "none";
    }
    // Restablecer campos deshabilitados
        recurrencia.disabled = true;
        cuotas.disabled = true;
});



