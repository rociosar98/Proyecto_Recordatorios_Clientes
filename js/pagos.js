import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const tablaPagos = document.getElementById("tablaPagos");
  const popupItems = document.getElementById("popupItems");
  const popupPago = document.getElementById("popupPago");
  const itemsList = document.getElementById("itemsList");
  const formPago = document.getElementById("formPago");
  const pagoMonto = document.getElementById("pagoMonto");
  const pagoFecha = document.getElementById("pagoFecha");
  const pagoObs = document.getElementById("pagoObs");
  let servicioClienteSeleccionado = null;

  const token = sessionStorage.getItem("token");

  async function cargarResumenPagos() {
    try {
      const res = await fetch("http://localhost:8000/pagos/resumen", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Error al cargar resumen de pagos");
      const resumenes = await res.json();

      tablaPagos.innerHTML = "";
      resumenes.forEach(r => {
        const tr = document.createElement("tr");
        tr.className = r.estado;
        tr.innerHTML = `
          <td>${r.cliente_nombre} / ${r.empresa} 
            <button class="ver-items" data-id="${r.servicio_cliente_id}">📄</button>
          </td>
          <td>${r.servicio}</td>
          <td>$${r.monto_total?.toLocaleString() || "-"}</td>
          
          <td>$${r.total_pagado?.toLocaleString() || "-"}</td>
          <td>$${r.saldo?.toLocaleString() || "-"}</td>
          <td class="saldo-favor">${r.saldo_a_favor > 0 ? "$" + r.saldo_a_favor?.toLocaleString() : "-"}</td>
          <td>
            <button class="registrar-pago" data-id="${r.servicio_cliente_id}">Registrar Pago</button>
          </td>
        `;
        tablaPagos.appendChild(tr);
      });

    } catch (err) {
      alert(err.message);
    }
  }

  cargarResumenPagos();

  // Delegación de eventos
tablaPagos.addEventListener("click", async (e) => {
  if (e.target.classList.contains("ver-items")) {
    const id = e.target.dataset.id;
    servicioClienteSeleccionado = id;

    try {
      const res = await fetch(`http://localhost:8000/pagos/items/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      let items = [];
      if (!res.ok) {
        // Si la petición falla
        itemsList.innerHTML = "<li>No se pudieron obtener los ítems.</li>";
      } else {
        // Si la petición fue ok, obtenemos los datos
        items = await res.json();

        if (items.length === 0) {
          // Si el array está vacío
          itemsList.innerHTML = "<li>No hay ítems generados este mes.</li>";
        } else {
          // Si hay ítems
          itemsList.innerHTML = items
            .map(item => `<li>${item.descripcion} - $${item.monto.toLocaleString('es-AR')}</li>`)
            .join("");
        }
      }
    } catch (err) {
      console.error("Error al obtener ítems:", err);
      itemsList.innerHTML = "<li>Error al cargar los ítems del mes.</li>";
    }

    popupItems.style.display = "block";

  } else if (e.target.classList.contains("registrar-pago")) {
    servicioClienteSeleccionado = e.target.dataset.id;
    popupPago.style.display = "block"; // solo aquí se abre
  }
});


      //if (!res.ok) {
        //itemsList.innerHTML = "<li>No se encontraron ítems para este mes</li>";
      //} else {
        //const items = await res.json();
        //itemsList.innerHTML = items
          //.map(item => `<li>${item.descripcion} - $${item.monto.toLocaleString('es-AR')}</li>`)
          //.join("");
      //}

      // Traer items del mes (simulado aquí)
      //itemsList.innerHTML = "<li>Item 1</li><li>Item 2</li>"; // reemplazar con fetch si hay endpoint
      //popupItems.style.display = "block";
    //} else if (e.target.classList.contains("registrar-pago")) {
      //servicioClienteSeleccionado = e.target.dataset.id;
      //popupPago.style.display = "block";
    //}
  //});

  // Cerrar popups
  document.querySelectorAll(".close-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.parentElement.parentElement.style.display = "none";
    });
  });

  // Formulario de pago
  formPago.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = {
        servicio_cliente_id: parseInt(servicioClienteSeleccionado),
        monto: parseFloat(pagoMonto.value),
        fecha_facturacion: pagoFecha.value,
        fecha_pago: pagoFecha.value,
        observaciones: pagoObs.value
      };

      const res = await fetch("http://localhost:8000/pagos/registrar", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errBody = await res.json();
        throw new Error(errBody.detail || "Error al registrar pago");
      }

      alert("Pago registrado exitosamente");
      formPago.reset();
      popupPago.style.display = "none";
      await cargarResumenPagos();

    } catch (err) {
      alert("Error: " + err.message);
    }
  });


  // BOTONES DE RECORDATORIOS
  const btnRecordatorio10 = document.getElementById("btnRecordatorio");
  const btnMora20 = document.getElementById("btnMora");
  const btnCorte28 = document.getElementById("btnCorte");

  async function enviarRecordatorios(url, mensajeConfirmacion) {
    if (!confirm("¿Estás seguro de enviar los recordatorios?")) return;
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
      const data = await res.json();
      alert(mensajeConfirmacion + "\n\n" + data.message);
    } catch (err) {
      alert("Error al enviar recordatorios: " + err.message);
    }
  }

  if (btnRecordatorio10) {
    btnRecordatorio10.addEventListener("click", () => 
      enviarRecordatorios("http://localhost:8000/recordatorios/generar-dia-10", "Recordatorios de día 10 enviados correctamente.")
    );
  }

  if (btnMora20) {
    btnMora20.addEventListener("click", () => 
      enviarRecordatorios("http://localhost:8000/recordatorios/generar-mora", "Alertas de mora (día 20) enviadas correctamente.")
    );
  }

  if (btnCorte28) {
    btnCorte28.addEventListener("click", () => 
      enviarRecordatorios("http://localhost:8000/recordatorios/generar-corte", "Avisos de corte (día 28) enviados correctamente.")
    );
  }
});
