import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario"));

  const saludo = document.getElementById("adminSaludo");
  const clienteSelect = document.getElementById("clienteSelect");
  const servicioSelect = document.getElementById("servicioSelect");
  const asignarForm = document.getElementById("crudForm");  // reutiliza id “crudForm”
  const tablaAsignaciones = document.getElementById("tablaAsignaciones");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
  }

  // Carga inicial de clientes y servicios
  await cargarClientes();
  await cargarServicios();
  await cargarAsignaciones();

  asignarForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const clienteId = clienteSelect.value;
    const servicioId = servicioSelect.value;

    if (!clienteId || !servicioId) {
      alert("Por favor seleccioná un Cliente y un Servicio.");
      return;
    }

    const payload = {
      cliente_id: parseInt(clienteId),
      servicio_id: parseInt(servicioId)
    };

    try {
      const res = await fetch("http://localhost:8000/servicios_clientes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errBody = await res.json();
        throw new Error(errBody.detail || "Error al asignar servicio");
      }

      alert("Servicio asignado correctamente");
      asignarForm.reset();
      await cargarAsignaciones();

    } catch (err) {
      alert("Error: " + err.message);
    }
  });

  // Función: cargar lista de clientes
  async function cargarClientes() {
    try {
      const res = await fetch("http://localhost:8000/clientes", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("No se pudieron obtener los clientes");
      const clientes = await res.json();

      clienteSelect.innerHTML = `<option value="" disabled selected>Seleccionar Cliente</option>`;
      clientes.forEach(c => {
        clienteSelect.innerHTML += `<option value="${c.id}">${c.nombre} ${c.apellido} — ${c.empresa}</option>`;
      });

    } catch (err) {
      alert("Error al cargar clientes: " + err.message);
    }
  }

  // Función: cargar lista de servicios
  async function cargarServicios() {
    try {
      const res = await fetch("http://localhost:8000/servicios", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("No se pudieron obtener los servicios");
      const servicios = await res.json();

      servicioSelect.innerHTML = `<option value="" disabled selected>Seleccionar Servicio</option>`;
      servicios.forEach(s => {
        servicioSelect.innerHTML += `<option value="${s.id}">${s.nombre} — $${s.precio}</option>`;
      });

    } catch (err) {
      alert("Error al cargar servicios: " + err.message);
    }
  }

  // Función: cargar asignaciones actuales (servicios por cliente)
  async function cargarAsignaciones() {
    try {
      const res = await fetch("http://localhost:8000/servicios_clientes", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("No se pudieron obtener las asignaciones");
      const asignaciones = await res.json();

      tablaAsignaciones.innerHTML = "";
      asignaciones.forEach(a => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${a.cliente_nombre || "-"}</td>
          <td>${a.servicio_nombre || "-"}</td>
          <td>${a.precio_congelado != null ? '$'+a.precio_congelado : "-"}</td>
          <td>${a.fecha_inicio || "-"}</td>
          <td>
            <button class="btn-borrar" data-id="${a.id}">Desasignar</button>
          </td>
        `;
        tablaAsignaciones.appendChild(tr);
      });

      // Agregar evento para botón “Desasignar”
      document.querySelectorAll(".btn-borrar").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.getAttribute("data-id");
          if (!confirm("¿Segur@ que querés desasignar este servicio?")) return;
          try {
            const resDel = await fetch(`http://localhost:8000/servicios_clientes/${id}`, {
              method: "DELETE",
              headers: { Authorization: `Bearer ${token}` }
            });
            if (!resDel.ok) {
              const errBody = await resDel.json();
              throw new Error(errBody.detail || "Error al desasignar servicio");
            }
            alert("Servicio desasignado");
            await cargarAsignaciones();
          } catch (err) {
            alert("Error: " + err.message);
          }
        });
      });

    } catch (err) {
      alert("Error al cargar asignaciones: " + err.message);
    }
  }

});
