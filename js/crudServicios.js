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

    let servicioSeleccionadoId = null; //Guarda el ID del servicio seleccionado para editar o eliminar. Está vacío al inicio.

    if (usuario) {
        saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
    }

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
                    <td>${s.recurrencia ?? ''}</td>
                    <td>${s.cuotas ?? ''}</td>
                    </tr>`;
            });

            document.querySelectorAll("#serviciosTabla tr").forEach(row => { //Después de llenar la tabla, esta línea selecciona todas las filas (<tr>) que estén dentro del elemento con id serviciosTabla, y las recorre una por una.
                row.addEventListener("click", () => { //A cada fila le agrega un evento click. O sea, cuando el usuario hace clic en una fila de la tabla
                    const id = row.getAttribute("data-id"); //Toma el atributo data-id que habías puesto antes en la fila y lo guarda en una variable.
                    seleccionarServicio(id);
                });
            });

        } catch (err) {
            alert("Error: " + err.message); 
        } // Agrega un evento click a cada fila para que, al hacer clic, se llame a seleccionarServicio(id) con el ID correspondiente.
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
            document.getElementById("recurrencia").value = servicio.recurrencia ?? "";
            document.getElementById("cuotas").value = servicio.cuotas ?? "";
            // Rellena los campos del formulario HTML con los datos del destino seleccionado, para que el usuario pueda editarlos.

            tipoServicio.dispatchEvent(new Event("change")); // Dispara el cambio para activar/desactivar campos

            servicioSeleccionadoId = id;

            btnCrear.style.display = "none";
            btnActualizar.style.display = "inline";
            btnEliminar.style.display = "inline";

        } catch (err) {
            alert("Error: " + err.message);
        }
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); //Evita que el formulario haga su comportamiento por defecto (recargar la página o enviar datos de forma tradicional).
        // Al enviar el formulario, previene el comportamiento por defecto y se asegura de que no haya un servicio seleccionado (porque en ese caso se actualizaría, no se crearía uno nuevo).

        if (servicioSeleccionadoId) return;

        const nombre = document.getElementById("nombre").value.trim();
        const precio = parseFloat(document.getElementById("precio").value);
        const tipo = document.getElementById("tipo").value;
        const recurrenciaVal = (tipo === "recurrente") ? document.getElementById("recurrencia").value || null : null;
        const cuotasVal = (tipo === "pago_unico") ? parseInt(document.getElementById("cuotas").value) || null : null;

        const nuevoServicio = {
            nombre,
            precio,
            tipo,
            recurrencia: recurrenciaVal,
            cuotas: cuotasVal,
            activo: true
        }; // Crea un objeto con los datos del nuevo destino, tomados desde los inputs del formulario HTML.

        console.log("Payload para crear servicio:", nuevoServicio);

        try {
            const res = await fetch("http://localhost:8000/servicios", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}` //Se pasan los headers necesarios: tipo de contenido y token de autenticación.
                },
                body: JSON.stringify(nuevoServicio) // Se convierte el objeto JS (nuevoServicio) a texto JSON con JSON.stringify().
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || "Error al crear servicio");
            }

            alert("Servicio creado correctamente");
            form.reset();
            await cargarServicios();
        } catch (err) {
            alert("Error: " + err.message);
        } // Envía los datos al backend para crear el nuevo servicio. Si todo sale bien, muestra mensaje, limpia el form y recarga la tabla.
    });

    btnActualizar.addEventListener("click", async () => {
        if (!servicioSeleccionadoId) return; //Si no hay servicio seleccionado, se sale de la funcion

        const nombre = document.getElementById("nombre").value.trim();
        const precio = parseFloat(document.getElementById("precio").value);
        const tipo = document.getElementById("tipo").value;
        const recurrenciaVal = recurrencia.disabled ? null : document.getElementById("recurrencia").value || null;
        const cuotasVal = cuotas.disabled ? null : parseInt(document.getElementById("cuotas").value) || null;

        const servicioActualizado = {
            nombre,
            precio,
            tipo,
            recurrencia: recurrenciaVal,
            cuotas: cuotasVal,
            activo: true
        }; //Se toma la información actual del formulario y se construye un objeto con los datos nuevos o modificados del servicio.

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
        }
    });

    btnEliminar.addEventListener("click", async () => {
        if (!servicioSeleccionadoId) return;

        if (!confirm("¿Estás seguro de eliminar este servicio?")) return; //Si no hay servicio seleccionado o el usuario no confirma, no hace nada.

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

        // Restablecer campos deshabilitados
        recurrencia.disabled = true;
        cuotas.disabled = true;
    }

    // Inicializa campos deshabilitados al cargar la página
    recurrencia.disabled = true;
    cuotas.disabled = true;
});
