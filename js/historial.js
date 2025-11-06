import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const tabla = document.getElementById("tablaHistorial");
  const mensajeVacio = document.getElementById("mensajeVacio");
  const filtroCliente = document.getElementById("filtroCliente");
  const filtroEstado = document.getElementById("filtroEstado");
  const filtroMes = document.getElementById("filtroMes");
  const filtroAnio = document.getElementById("filtroAnio");
  const fechaDesde = document.getElementById("fechaDesde");
  const fechaHasta = document.getElementById("fechaHasta");
  // btnBuscar = document.getElementById("btnBuscar");

  let datosHistorial = []; // Guardamos todos los datos aquí

  // Al cargar la página, mostrar todo
  await cargarHistorial();

  async function cargarHistorial(clienteId = null) {
    try {
      const url = new URL("http://localhost:8000/historial");
      if (clienteId) url.searchParams.append("cliente_id", clienteId);

      const res = await fetchConAuth(url.href);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error ${res.status}`);
      }

      datosHistorial = await res.json();
      aplicarFiltros(); // renderizamos filtrado
    } catch (err) {
      console.error("Error al cargar historial:", err);
      alert("Error al cargar historial: " + err.message);
    }
  }

  function aplicarFiltros() {
    const clienteTexto = filtroCliente.value.trim().toLowerCase();
    const estadoSeleccionado = filtroEstado.value;
    const mesSeleccionado = filtroMes.value; // YYYY-MM
    const anioSeleccionado = filtroAnio.value; // YYYY
    const desde = fechaDesde.value; // YYYY-MM-DD
    const hasta = fechaHasta.value; // YYYY-MM-DD

    const filtrado = datosHistorial.filter(pago => {
      // filtrar por clientes
      const nombreCliente = `${pago.cliente?.nombre || ""} ${pago.cliente?.apellido || ""}`.toLowerCase();
      const coincideCliente = clienteTexto ? nombreCliente.includes(clienteTexto) : true;

      // filtrar por estado
      const coincideEstado = estadoSeleccionado ? pago.estado === estadoSeleccionado : true;

      // filtrar por fechas
      let coincideFecha = true;

      if (desde && hasta && pago.fecha_facturacion) {
      // Filtrar por rango de fechas
        coincideFecha = pago.fecha_facturacion >= desde && pago.fecha_facturacion <= hasta;
      } else if (mesSeleccionado && pago.fecha_facturacion) {
      // Filtrar por mes seleccionado (YYYY-MM)
        const [anioPago, mesPago] = pago.fecha_facturacion.split("-");
        const [anioSel, mesSel] = mesSeleccionado.split("-");
        coincideFecha = anioPago === anioSel && mesPago === mesSel;
      } else if (anioSeleccionado && pago.fecha_facturacion) {
      // Filtrar solo por año
        const anioPago = pago.fecha_facturacion.split("-")[0];
        coincideFecha = anioPago === anioSeleccionado;
      }

      return coincideCliente && coincideEstado && coincideFecha;
    });

    renderHistorial(filtrado);
  }

  function renderHistorial(data) {
    tabla.innerHTML = "";

    if (!Array.isArray(data) || data.length === 0) {
      mensajeVacio.style.display = "block";
      return;
    } else {
      mensajeVacio.style.display = "none";
    }

    data.forEach(pago => {
      const clienteNombre = `${pago.cliente?.nombre || ""} ${pago.cliente?.apellido || ""}`.trim() || "-";
      const clienteEmpresa = pago.cliente?.empresa || "-";
      const servicioNombre = pago.servicio || "-";
      const monto = pago.monto?.toLocaleString() || "-";
      const fechaFacturacion = pago.fecha_facturacion || "-";
      const fechaPago = pago.fecha_pago || "-";
      const estado = pago.estado || "-";

      let estadoClase = "";
      if (estado === "pagado") estadoClase = "estado-pagado";
      else if (estado === "parcial") estadoClase = "estado-parcial";
      else if (estado === "pendiente") estadoClase = "estado-pendiente";

      const tr = document.createElement("tr");
      tr.classList.add(estadoClase);

      tr.innerHTML = `
        <td>${clienteNombre}</td>
        <td>${clienteEmpresa}</td>
        <td>${servicioNombre}</td>
        <td>$${monto}</td>
        <td>${fechaFacturacion}</td>
        <td>${fechaPago}</td>
        <td class="estado ${estado}">${estado}</td>
      `;
      tabla.appendChild(tr);
    });
  }

  // Evento botón Buscar: carga y aplica filtros
  btnBuscar.addEventListener("click", async () => {
    await cargarHistorial(); // Refresca y vuelve a aplicar
  });

  // Eventos en filtros en tiempo real
  filtroCliente.addEventListener("input", aplicarFiltros);
  filtroEstado.addEventListener("change", aplicarFiltros);
  filtroMes.addEventListener("change", aplicarFiltros);
  filtroAnio.addEventListener("input", aplicarFiltros);
  fechaDesde.addEventListener("change", aplicarFiltros);
  fechaHasta.addEventListener("change", aplicarFiltros);
});

