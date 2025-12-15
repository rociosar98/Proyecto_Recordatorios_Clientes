import { fetchConAuth } from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
  const tablaPagos = document.getElementById("tablaPagos");
  const popupPago = document.getElementById("popupPago");
  const formPago = document.getElementById("formPago");
  const pagoMonto = document.getElementById("pagoMonto");
  const pagoFecha = document.getElementById("pagoFecha");
  const pagoObs = document.getElementById("pagoObs");
  let servicioClienteSeleccionado = null;

  const token = sessionStorage.getItem("token");

  const today = new Date();
  const anio = today.getFullYear();
  const mes = today.getMonth() + 1; // Enero = 0

  //CARGAR RESUMEN DE PAGOS
  async function cargarResumenPagos() {
    try {
      const res = await fetch("http://localhost:8000/pagos/resumen", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!res.ok) throw new Error("Error al cargar resumen de pagos");

      const data = await res.json();
      tablaPagos.innerHTML = "";

      data.forEach(pago => {
        const tr = document.createElement("tr");
        tr.className = pago.estado;

        tr.innerHTML = `
          <td>${pago.cliente_nombre} / ${pago.empresa}</td>
          <td>${pago.servicio}</td>
          <td>$${pago.monto_total?.toLocaleString() || "-"}</td>
          <td>$${pago.total_pagado?.toLocaleString() || "-"}</td>
          <td>$${pago.saldo?.toLocaleString() || "-"}</td>
          <td class="saldo-favor">${pago.saldo_a_favor > 0 ? "$" + pago.saldo_a_favor.toLocaleString() : "-"}</td>
          <td>
            <button class="registrar-pago" data-id="${pago.servicio_cliente_id}">Registrar Pago</button>
          </td>
        `;
        tablaPagos.appendChild(tr);
      });

    } catch (err) {
      alert(err.message);
    }
  }

  cargarResumenPagos();



//   async function cargarPagosPorMes(anio, mes) {
//     try {
//       const res = await fetch(`http://localhost:8000/pagos/mensuales?anio=${anio}&mes=${mes}`, {
//         headers: { Authorization: `Bearer ${token}` }
//       });

//       if (!res.ok) throw new Error("Error al cargar pagos mensuales");
//       const data = await res.json();

//       //console.log("Respuesta completa del backend:", data); // <-- NUEVO

//       //const pagos = data[0]?.pagos || [];
//       const pagos = Array.isArray(data) ? data : [];
//       //console.log("Pagos extraídos:", pagos); // <-- NUEVO
//       tablaPagos.innerHTML = "";

//       pagos.forEach(pago => {
//         // Crear encabezado del mes
//         console.log("Pago mensual recibido:", pago); // <-- NUEVO
//         const tr = document.createElement("tr");
//         tr.className = pago.estado; // pendiente, parcial, pagado

//         // Nota: total_pagado, saldo, saldo_a_favor no vienen, usamos defaults
//         const montoMes = pago.monto_mes ?? 0;
//         const totalPagadoMes = pago.total_pagado_mes || 0;
//         const saldoMes = pago.saldo_mes ?? 0;
//         //const saldo = pago.monto - totalPagado;
//         const saldoAFavor = pago.saldo_a_favor || 0;

//         tr.innerHTML = `
//           <td>${pago.cliente.nombre} ${pago.cliente.apellido} / ${pago.cliente.empresa}</td>
//           <td>${pago.servicio.nombre}</td>
//           <td>$${montoMes?.toLocaleString() || "-"}</td>
//           <td>$${totalPagadoMes.toLocaleString()}</td>
//           <td>$${saldoMes.toLocaleString()}</td>
//           <td class="saldo-favor">${saldoAFavor > 0 ? "$" + saldoAFavor.toLocaleString() : "-"}</td>
//           <td>
//             <button class="registrar-pago" data-id="${pago.servicio_cliente_id}">Registrar Pago</button>
//           </td>
//         `;
//         tablaPagos.appendChild(tr);
//       });

//     } catch (err) {
//     alert(err.message);
//   }
// }

// // cargar pagos del mes actuall
// cargarPagosPorMes(anio, mes);




  //       const tr = document.createElement("tr");
  //       tr.className = r.estado;
  //       tr.innerHTML = `
  //         <td>${r.cliente_nombre} / ${r.empresa}</td>
  //         <td>${r.servicio}</td>
  //         <td>$${r.monto_total?.toLocaleString() || "-"}</td>
          
  //         <td>$${r.total_pagado?.toLocaleString() || "-"}</td>
  //         <td>$${r.saldo?.toLocaleString() || "-"}</td>
  //         <td class="saldo-favor">${r.saldo_a_favor > 0 ? "$" + r.saldo_a_favor?.toLocaleString() : "-"}</td>
  //         <td>
  //           <button class="registrar-pago" data-id="${r.servicio_cliente_id}">Registrar Pago</button>
  //         </td>
  //       `;
  //       tablaPagos.appendChild(tr);
  //     });

  //   } catch (err) {
  //     alert(err.message);
  //   }
  // }

  //cargarResumenPagos();

  // Delegación de eventos
  tablaPagos.addEventListener("click", (e) => {
    if (e.target.classList.contains("registrar-pago")) {
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
      // cargarPagosPorMes(anio, mes);
      //cargarResumenPagos();

    } catch (err) {
      alert("Error: " + err.message);
    }
  });

  // --- Inicializar ---
//   cargarPagosPorMes(anio, mes);
// });


botones.forEach(({ btn, url, msg }) => {
  if (btn) {
    btn.addEventListener("click", () => enviarRecordatorios(url, msg));
  }
});


  // BOTONES DE RECORDATORIOS
//   const btnRecordatorio10 = document.getElementById("btnRecordatorio");
//   const btnMora20 = document.getElementById("btnMora");
//   const btnCorte28 = document.getElementById("btnCorte");

//   async function enviarRecordatorios(url, mensajeConfirmacion) {
//     if (!confirm("¿Estás seguro de enviar los recordatorios?")) return;
//     try {
//       const res = await fetch(url, {
//         method: "POST",
//         headers: {
//           "Authorization": `Bearer ${token}`,
//           "Content-Type": "application/json"
//         }
//       });
//       const data = await res.json();
//       alert(mensajeConfirmacion + "\n\n" + data.message);
//     } catch (err) {
//       alert("Error al enviar recordatorios: " + err.message);
//     }
//   }

//   if (btnRecordatorio10) {
//     btnRecordatorio10.addEventListener("click", () => 
//       enviarRecordatorios("http://localhost:8000/recordatorios/generar-dia-10", "Recordatorios de día 10 enviados correctamente.")
//     );
//   }

//   if (btnMora20) {
//     btnMora20.addEventListener("click", () => 
//       enviarRecordatorios("http://localhost:8000/recordatorios/generar-mora", "Alertas de mora (día 20) enviadas correctamente.")
//     );
//   }

//   if (btnCorte28) {
//     btnCorte28.addEventListener("click", () => 
//       enviarRecordatorios("http://localhost:8000/recordatorios/generar-corte", "Avisos de corte (día 28) enviados correctamente.")
//     );
//   }
 });

