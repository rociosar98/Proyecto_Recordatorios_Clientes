import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", () => {
  const tabla = document.getElementById("tablaListado");
  const filtroIVA = document.getElementById("filtroIVA");
  const filtroResponsable = document.getElementById("filtroResponsable");
  const btnBuscar = document.getElementById("btnBuscar");
  const mensajeVacio = document.getElementById("mensajeVacio");

  async function cargarListado() {
    const iva = filtroIVA.value;
    const responsable = filtroResponsable.value.trim();

    const url = new URL("http://localhost:8000/listado-mensual");

    if (iva) {
      url.searchParams.append("condicion_iva", iva);
    }

    if (responsable) {
      url.searchParams.append("responsable_cuenta", responsable);
    }

    try {
      const res = await fetchConAuth(url.href);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();

      // Ordenamos manualmente: primero por responsable, luego por cliente
      data.sort((a, b) => {
        const r1Nombre = a.cliente?.responsable?.nombre?.toLowerCase() || "";
        const r1Apellido = a.cliente?.responsable?.apellido?.toLowerCase() || "";
        const r2Nombre = b.cliente?.responsable?.nombre?.toLowerCase() || "";
        const r2Apellido = b.cliente?.responsable?.apellido?.toLowerCase() || "";

        const nombreCompleto1 = `${r1Apellido} ${r1Nombre}`;
        const nombreCompleto2 = `${r2Apellido} ${r2Nombre}`;

        const compareResponsable = nombreCompleto1.localeCompare(nombreCompleto2);
        if (compareResponsable !== 0) return compareResponsable;

        const e1 = (a.cliente?.empresa || "").toLowerCase();
        const e2 = (b.cliente?.empresa || "").toLowerCase();

        return e1.localeCompare(e2);

      });

      renderTabla(data);
    } catch (error) {
      console.error("Error al cargar listado mensual:", error);
      alert("Error al cargar el listado mensual: " + error.message);
    }
  }

  function renderTabla(data) {
    tabla.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      mensajeVacio.style.display = "block";
      return;
    } else {
      mensajeVacio.style.display = "none";
    }

    data.forEach(pago => {
      const tr = document.createElement("tr");

      const estadoClase =
        pago.estado === "pagado"
          ? "estado-pagado"
          : pago.estado === "parcial"
          ? "estado-parcial"
          : "estado-pendiente";

      tr.classList.add(estadoClase);

      tr.innerHTML = `
        <td>${pago.cliente?.nombre || "-"}</td>
        <td>${pago.cliente?.condicion_iva || "-"}</td>
        <td>${pago.cliente?.responsable?.nombre || ""} ${pago.cliente?.responsable?.apellido || "-"}</td>
        <td>${pago.servicio?.nombre || "-"}</td>
        <td>${pago.fecha_facturacion || "-"}</td>
        <td>${pago.fecha_pago || "-"}</td>
        <td>$${pago.monto?.toLocaleString() || "-"}</td>
        <td>${pago.estado}</td>
      `;

      tabla.appendChild(tr);
    });
  }

  btnBuscar.addEventListener("click", cargarListado);

  cargarListado(); // Se carga automáticamente al abrir la página
});





/*
import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", () => {
  const tabla = document.getElementById("tablaListado");
  const filtroIVA = document.getElementById("filtroIVA");
  const filtroResponsable = document.getElementById("filtroResponsable");
  const btnBuscar = document.getElementById("btnBuscar");
  const mensajeVacio = document.getElementById("mensajeVacio");

  // Función principal para cargar datos
  async function cargarListado() {
    const iva = filtroIVA.value;
    const responsable = filtroResponsable.value.trim();

    const url = new URL("http://localhost:8000/listado-mensual");

    if (iva) {
      url.searchParams.append("condicion_iva", iva);
    }

    if (responsable) {
      url.searchParams.append("responsable_cuenta", responsable);
    }

    try {
      const res = await fetchConAuth(url.href);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();
      renderTabla(data);
    } catch (error) {
      console.error("Error al cargar listado mensual:", error);
      alert("Error al cargar el listado mensual: " + error.message);
    }
  }

  // Función que renderiza la tabla
  function renderTabla(data) {
    tabla.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      mensajeVacio.style.display = "block";
      return;
    } else {
      mensajeVacio.style.display = "none";
    }

    data.forEach(pago => {
      const tr = document.createElement("tr");

      const estadoClase =
        pago.estado === "pagado"
          ? "estado-pagado"
          : pago.estado === "parcial"
          ? "estado-parcial"
          : "estado-pendiente";

      tr.classList.add(estadoClase);

      tr.innerHTML = `
        <td>${pago.cliente?.nombre || "-"}</td>
        <td>${pago.cliente?.condicion_iva || "-"}</td>
        <td>${pago.cliente?.responsable_id || "-"}</td>
        <td>${pago.servicio?.nombre || "-"}</td>
        <td>${pago.fecha_facturacion || "-"}</td>
        <td>${pago.fecha_pago || "-"}</td>
        <td>$${pago.monto?.toLocaleString() || "-"}</td>
        <td>${pago.estado}</td>
      `;

      tabla.appendChild(tr);
    });
  }

  btnBuscar.addEventListener("click", cargarListado);

  // Cargar al inicio
  cargarListado();
});
*/