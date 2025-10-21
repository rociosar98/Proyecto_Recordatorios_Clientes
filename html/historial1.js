const datosHistorial = [
  {
    cliente: "Juan Pérez",
    empresa: "Tech Solutions",
    fechaFacturacion: "2025-09-01",
    fechaPago: "2025-09-03",
    monto: 12000,
    estado: "pagado"
  },
  {
    cliente: "Ana Torres",
    empresa: "Distribuciones Torres",
    fechaFacturacion: "2025-09-01",
    fechaPago: null,
    monto: 9000,
    estado: "impago"
  },
  {
    cliente: "Carlos Gómez",
    empresa: "Gómez Construcciones",
    fechaFacturacion: "2025-09-01",
    fechaPago: "2025-09-10",
    monto: 5000,
    estado: "parcial"
  }
];

const tabla = document.getElementById("tablaHistorial");
const filtroCliente = document.getElementById("filtroCliente");
const filtroEstado = document.getElementById("filtroEstado");

function renderTabla(datos) {
  tabla.innerHTML = "";
  datos.forEach(dato => {
    const tr = document.createElement("tr");
    tr.classList.add(`estado-${dato.estado}`);

    tr.innerHTML = `
      <td>${dato.cliente}</td>
      <td>${dato.empresa}</td>
      <td>${dato.fechaFacturacion}</td>
      <td>${dato.fechaPago || "-"}</td>
      <td>$${dato.monto.toLocaleString()}</td>
      <td>${dato.estado.charAt(0).toUpperCase() + dato.estado.slice(1)}</td>
    `;

    tabla.appendChild(tr);
  });
}

function aplicarFiltros() {
  const cliente = filtroCliente.value.toLowerCase();
  const estado = filtroEstado.value;

  const filtrado = datosHistorial.filter(dato => {
    const coincideCliente = dato.cliente.toLowerCase().includes(cliente);
    const coincideEstado = estado ? dato.estado === estado : true;
    return coincideCliente && coincideEstado;
  });

  renderTabla(filtrado);
}

filtroCliente.addEventListener("input", aplicarFiltros);
filtroEstado.addEventListener("change", aplicarFiltros);

// Inicial
renderTabla(datosHistorial);
