import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario"));

  const saludo = document.getElementById("adminSaludo");
  const clienteSelect = document.getElementById("clienteSelect");
  const servicioSelect = document.getElementById("servicioSelect");
  const asignarForm = document.getElementById("crudForm");
  const tablaAsignaciones = document.getElementById("tablaAsignaciones");
  const cuotasContainer = document.getElementById("cuotasContainer");
  const cuotasSelect = document.getElementById("cuotasSelect");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
  }

  // Carga inicial
  await cargarClientes();
  await cargarServicios();
  await cargarAsignaciones();

  // Mostrar/ocultar cuotas según tipo de servicio
  servicioSelect.addEventListener("change", async () => {
    const servicioId = parseInt(servicioSelect.value);
    if (!servicioId) return;

    try {
      const res = await fetch(`http://localhost:8000/servicios/${servicioId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("No se pudo obtener el servicio");
      const servicio = await res.json();

      if (servicio.tipo === "pago_unico") {
        cuotasContainer.style.display = "block";
      } else {
        cuotasContainer.style.display = "none";
        cuotasSelect.value = "";
      }
    } catch (err) {
      alert("Error al cargar servicio: " + err.message);
    }
  });

  // Submit asignar servicio
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
      servicio_id: parseInt(servicioId),
      cuotas: cuotasSelect.value ? parseInt(cuotasSelect.value) : null
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
      cuotasContainer.style.display = "none";
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

  // Función: cargar asignaciones actuales
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
          <td>${a.cliente_nombre || "-"} ${a.cliente_apellido || ""}</td>
          <td>${a.servicio_nombre || "-"}</td>
          <td>${a.precio_congelado != null ? '$'+a.precio_congelado : "-"}</td>
          <td>${formatearFecha(a.fecha_inicio)}</td>
          <td>${a.fecha_vencimiento ? formatearFecha(a.fecha_vencimiento) : "-"}</td>
          <td>${a.cuotas != null ? a.cuotas : "-"}</td>
          <td>
            <button class="btn-borrar" data-id="${a.id}">Desasignar</button>
          </td>
        `;
        tablaAsignaciones.appendChild(tr);
      });

    } catch (err) {
      alert("Error al cargar asignaciones: " + err.message);
    }
  }

  // Delegación de eventos para desasignar
  tablaAsignaciones.addEventListener("click", async (e) => {
    if (!e.target.classList.contains("btn-borrar")) return;

    const id = e.target.getAttribute("data-id");
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

  // Función para formatear fechas
  function formatearFecha(fechaStr) {
    if (!fechaStr) return "-";
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString("es-AR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  }

});
