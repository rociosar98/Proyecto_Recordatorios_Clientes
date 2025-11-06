import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", () => {
  const tabla = document.getElementById("tablaListado");
  const filtroIVA = document.getElementById("filtroIVA");
  const filtroResponsable = document.getElementById("filtroResponsable");
  const btnBuscar = document.getElementById("btnBuscar");
  const btnEnviarResúmenes = document.getElementById("btnEnviarResúmenes");
  const mensajeVacio = document.getElementById("mensajeVacio");

  let datosListado = []; // Guardamos todos los registros cargados

  // Carga inicial del listado completo
  cargarListado();

  async function cargarListado() {
    const iva = filtroIVA.value;
    const responsable = filtroResponsable.value.trim();

    const url = new URL("http://localhost:8000/listado-mensual");
    if (iva) url.searchParams.append("condicion_iva", iva);
    if (responsable) url.searchParams.append("responsable_nombre", responsable);

    try {
      const res = await fetchConAuth(url.href);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error ${res.status}`);
      }

      datosListado = await res.json();

      // Ordenar por responsable y luego por empresa
      datosListado.sort((a, b) => {
        const r1 = `${a.cliente?.responsable?.apellido || ""} ${a.cliente?.responsable?.nombre || ""}`.toLowerCase();
        const r2 = `${b.cliente?.responsable?.apellido || ""} ${b.cliente?.responsable?.nombre || ""}`.toLowerCase();
        const cmp = r1.localeCompare(r2);
        if (cmp !== 0) return cmp;
        return (a.cliente?.empresa || "").localeCompare(b.cliente?.empresa || "");
      });

      aplicarFiltros();
    } catch (error) {
      console.error("Error al cargar listado mensual:", error);
      alert("Error al cargar el listado mensual: " + error.message);
    }
  }

  // Filtrado en el front
  function aplicarFiltros() {
    const ivaSeleccionado = filtroIVA.value.trim().toLowerCase();
    const textoResponsable = filtroResponsable.value.trim().toLowerCase();

    const filtrado = datosListado.filter(pago => {
      const condicionIVA = (pago.cliente?.condicion_iva || "").trim().toLowerCase();
      const coincideIVA = ivaSeleccionado ? condicionIVA === ivaSeleccionado : true;

      const nombreResponsable = `${pago.cliente?.responsable?.nombre || ""} ${pago.cliente?.responsable?.apellido || ""}`.toLowerCase();
      const coincideResponsable = textoResponsable
        ? nombreResponsable.includes(textoResponsable)
        : true;

      return coincideIVA && coincideResponsable;
    });

    renderTabla(filtrado);
  }

  function renderTabla(data) {
    tabla.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      mensajeVacio.style.display = "block";
      return;
    } else {
      mensajeVacio.style.display = "none";
    }

    data.forEach(item => {
      const tr = document.createElement("tr");

      const estadoClase =
        item.estado === "pagado"
          ? "estado-pagado"
          : item.estado === "parcial"
          ? "estado-parcial"
          : "estado-pendiente";

      tr.classList.add(estadoClase);

      tr.innerHTML = `
        <td>${item.cliente?.nombre || ""} ${item.cliente?.apellido || ""}</td>
        <td>${item.cliente?.empresa || "-"}</td>
        <td>${item.cliente?.condicion_iva || "-"}</td>
        <td>${item.cliente?.responsable?.nombre || ""} ${item.cliente?.responsable?.apellido || "-"}</td>
        <td>${item.servicio?.nombre || "-"}</td>
        <td>${item.fecha_facturacion || "-"}</td>
        <td>$${item.monto?.toLocaleString() || "-"}</td>
        <td class="estado">${item.estado || "-"}</td>
      `;

      tabla.appendChild(tr);
    });
  }

  // Eventos
  filtroIVA.addEventListener("change", aplicarFiltros);
  filtroResponsable.addEventListener("input", aplicarFiltros);
  btnBuscar.addEventListener("click", cargarListado);

  // Envío de resúmenes
  btnEnviarResúmenes.addEventListener("click", async () => {
    if (!confirm("¿Desea enviar los resúmenes a todos los clientes?")) return;

    try {
      const res = await fetchConAuth("http://localhost:8000/resumenes/enviar", {
        method: "POST"
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();
      alert(`Se enviaron resúmenes a:\n- ${data.resumenes_enviados.join("\n- ")}`);
    } catch (err) {
      console.error("Error al enviar resúmenes:", err);
      alert("Error al enviar resúmenes: " + err.message);
    }
  });
});

