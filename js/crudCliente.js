import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario"));
  const saludo = document.getElementById("adminSaludo");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
  }

  const form = document.getElementById("crudForm");
  const tabla = document.getElementById("clientesTabla");
  const responsableSelect = document.getElementById("responsable_id");

  // Cargar responsables en el select
  async function cargarResponsables() {
    try {
      const res = await fetch("http://localhost:8000/usuarios", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("No se pudieron obtener los responsables");
      const data = await res.json();

      responsableSelect.innerHTML = `<option value="" disabled selected>Seleccionar responsable</option>`;
      data.forEach((r) => {
        responsableSelect.innerHTML += `<option value="${r.id}">${r.nombre} ${r.apellido}</option>`;
      });
    } catch (err) {
      alert("Error al cargar responsables: " + err.message);
    }
  }

  // Cargar clientes
  async function cargarClientes() {
    try {
      const res = await fetchConAuth("http://localhost:8000/clientes");

      if (!res.ok) throw new Error("No se pudieron obtener los clientes");
      const data = await res.json();

      tabla.innerHTML = "";
      data.forEach((c) => {
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
          <td>${c.responsable ? c.responsable.nombre + ' ' + c.responsable.apellido : ''}</td>
          
        `;

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

          responsableSelect.value = c.responsable ? String(c.responsable.id) : "";

          //responsableSelect.value = c.responsable ? c.responsable.id : "";

          // si c.responsable existe, usamos su id
          //if (c.responsable) {
            //responsableSelect.value = c.responsable.id;
          //} else {
            //responsableSelect.value = "";
          //}

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

  await cargarResponsables(); // primero cargamos el select
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
      responsable_id: parseInt(responsableSelect.value),
      activo: true,
    };

    try {
      const res = await fetch("http://localhost:8000/clientes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(nuevoCliente),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error("Error al crear el cliente: " + JSON.stringify(errorData));
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

  btnActualizar.addEventListener("click", async () => {
    const id = document.getElementById("clienteId").value;

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
      responsable_id: parseInt(responsableSelect.value),
      activo: true,
    };

    try {
      const res = await fetch(`http://localhost:8000/clientes/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(clienteActualizado),
      });

      const data = await res.json();

      if (!res.ok) {
        const detalle = data.detail || data;
        alert("Error al actualizar el cliente: " + JSON.stringify(detalle));
        return;
      }

      alert("Cliente actualizado correctamente");
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
          Authorization: `Bearer ${token}`,
        },
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
