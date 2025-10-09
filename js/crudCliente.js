import {fetchConAuth} from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
    const token = sessionStorage.getItem("token");
    const usuario = JSON.parse(sessionStorage.getItem("usuario"));
    const saludo = document.getElementById("adminSaludo");

    if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
    }

    const form = document.getElementById("crudForm");
    const tabla = document.getElementById("clientesTabla");

    // Listar usuarios
    async function cargarClientes() {
    try {
        const res = await fetchConAuth("http://localhost:8000/clientes");

        if (!res.ok) throw new Error("No se pudieron obtener los clientes");
        const data = await res.json();

        tabla.innerHTML = "";
        data.forEach(c => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <td>${c.nombre}</td>
            <td>${c.apellido}</td>
            <td>${c.empresa}</td>
            <td>${c.domicilio}</td>
            <td>${c.codigo_postal}</td>
            <td>${c.localidad}</td>
            <td>${c.provincia}</td>
            <td>${c.pais}</td>
            <td>${c.telefono}</td>
            <td>${c.whatsapp}</td>
            <td>${c.correo}</td>
            <td>${c.metodo_aviso}</td>
            <td>${c.condicion_iva}</td>
            <td>${c.responsable_id}</td>
            `;
            tr.dataset.id = c.id;
            tr.dataset.nombre = c.nombre;
            tr.dataset.apellido = c.apellido;
            tr.dataset.empresa = c.empresa;
            tr.dataset.domicilio = c.domicilio;
            tr.dataset.codigo_postal = c.codigo_postal;
            tr.dataset.localidad = c.localidad;
            tr.dataset.provincia = c.provincia;
            tr.dataset.pais = c.pais;
            tr.dataset.telefono = c.telefono;
            tr.dataset.whatsapp = c.whatsapp;
            tr.dataset.correo = c.correo;
            tr.dataset.metodo_aviso = c.metodo_aviso;
            tr.dataset.condicion_iva = c.condicion_iva;
            tr.dataset.responsable_id = c.responsable_id;

          tr.addEventListener("click", () => {

              document.getElementById("clienteId").value = c.id;
              document.getElementById("nombre").value = c.nombre;
              document.getElementById("apellido").value = c.apellido;
              document.getElementById("empresa").value = c.empresa;
              document.getElementById("domicilio").value = c.domicilio;
              document.getElementById("codigo_postal").value = c.codigo_postal;
              document.getElementById("localidad").value = c.localidad;
              document.getElementById("provincia").value = c.provincia;
              document.getElementById("pais").value = c.pais;
              document.getElementById("telefono").value = c.telefono;
              document.getElementById("whatsapp").value = c.whatsapp;
              document.getElementById("correo").value = c.correo;
              document.getElementById("metodo_aviso").value = c.metodo_aviso;
              document.getElementById("condicion_iva").value = c.condicion_iva;
              document.getElementById("responsable_id").value = c.responsable_id;

              form.querySelector("button[type='submit']").style.display = "none";
              btnActualizar.style.display = "inline-block";
              btnEliminar.style.display = "inline-block";
          });

          tabla.appendChild(tr);

        });
      } catch (err) {
        alert("Error al cargar los clientes: " + err.message);
      }
}


      await cargarClientes();

      form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nuevoCliente = {
          nombre: document.getElementById("nombre").value,
          apellido: document.getElementById("apellido").value,
          empresa: document.getElementById("empresa").value,
          domicilio: document.getElementById("domicilio").value,
          codigo_postal: document.getElementById("codigo_postal").value,
          localidad: document.getElementById("localidad").value,
          provincia: document.getElementById("provincia").value,
          pais: document.getElementById("pais").value,
          telefono: document.getElementById("telefono").value,
          whatsapp: document.getElementById("whatsapp").value,
          correo: document.getElementById("correo").value,
          metodo_aviso: document.getElementById("metodo_aviso").value,
          condicion_iva: document.getElementById("condicion_iva").value,
          responsable_id: parseInt(usuario?.id),
          activo: true
        };

        console.log(nuevoCliente)

        try {
          const res = await fetch("http://localhost:8000/clientes", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(nuevoCliente)
          });

          if (!res.ok) {
            const errorData = await res.json();
            console.error("Error detalle:", errorData);
            throw new Error("Error al crear el cliente");
        }

          alert("Cliente creado correctamente");
          form.reset();
          await cargarClientes();
        } catch (err) {
          alert("Error: " + err.message);
        }
      });

      
      
    const btnActualizar = document.getElementById("btnActualizar");
    const btnEliminar = document.getElementById("btnEliminar");

    // ACTUALIZAR USUARIO
    btnActualizar.addEventListener("click", async () => {
      const id = document.getElementById("clienteId").value;
      console.log("ID a actualizar:", id);

      if (!id) {
        alert("Seleccioná un cliente antes de actualizar");
        return;
    }

      const clienteActualizado = {
        nombre: document.getElementById("nombre").value,
        apellido: document.getElementById("apellido").value,
        empresa: document.getElementById("empresa").value,
        domicilio: document.getElementById("domicilio").value,
        codigo_postal: document.getElementById("codigo_postal").value,
        localidad: document.getElementById("localidad").value,
        provincia: document.getElementById("provincia").value,
        pais: document.getElementById("pais").value,
        telefono: document.getElementById("telefono").value,
        whatsapp: document.getElementById("whatsapp").value,
        correo: document.getElementById("correo").value,
        metodo_aviso: document.getElementById("metodo_aviso").value,
        condicion_iva: document.getElementById("condicion_iva").value,
        responsable_id: parseInt(usuario?.id),
        activo: true
      };

      console.log("Payload actualización:", clienteActualizado);

      try {
        const res = await fetch(`http://localhost:8000/clientes/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(clienteActualizado)
        });

        const data = await res.json();
        console.log("Respuesta del servidor:", res.status, data);

        if (!res.ok) {
      // Mostrar detalle de error
            const detalle = data.detail || data;
            alert("Error al actualizar el cliente: " + JSON.stringify(detalle));
            return;
        }

        alert("Cliente actualizado");
        form.reset();
        btnActualizar.style.display = "none";
        btnEliminar.style.display = "none";
        form.querySelector("button[type='submit']").style.display = "inline-block";
        await cargarClientes();
      } catch (err) {
        alert("Error: " + err.message);
      }
    });

    btnEliminar.addEventListener("click", async () => {
      const id = document.getElementById("clienteId").value;
      if (!confirm("¿Seguro que querés eliminar este cliente?")) return;

        try {
        const res = await fetch(`http://localhost:8000/clientes/${id}`, {
            method: "DELETE",
            headers: {
            Authorization: `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Error al eliminar el cliente");

        alert("Cliente eliminado");
        form.reset();
        btnActualizar.style.display = "none";
        btnEliminar.style.display = "none";
        form.querySelector("button[type='submit']").style.display = "inline-block";
        await cargarClientes();
        } catch (err) {
        alert("Error: " + err.message);
        }
    });

    });