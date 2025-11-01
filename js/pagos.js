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
      // Traer items del mes (simulado aquí)
      itemsList.innerHTML = "<li>Item 1</li><li>Item 2</li>"; // reemplazar con fetch si hay endpoint
      popupItems.style.display = "block";
    } else if (e.target.classList.contains("registrar-pago")) {
      servicioClienteSeleccionado = e.target.dataset.id;
      popupPago.style.display = "block";
    }
  });

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
});
