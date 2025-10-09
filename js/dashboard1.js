document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario")); //Toma el objeto usuario guardado como texto en sessionStorage y lo convierte a un objeto JavaScript con JSON.parse. Esto permite acceder luego a propiedades como usuario.nombre o usuario.apellido.

  const saludo = document.getElementById("adminSaludo");
  const statsContainer = document.getElementById("estadisticasContainer");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
  }

  try {
    const res = await fetch("http://localhost:8000/dashboard/admin", { //Realiza una solicitud (GET) al backend en la ruta /dashboard/admin.
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("Error al obtener estadísticas");

    const data = await res.json(); //Convierte la respuesta del servidor (que viene en formato JSON) en un objeto JavaScript que se guarda en la variable data.

    //muestra las estadisticas
    statsContainer.innerHTML = `
      <p><strong>Destinos cargados:</strong> ${data.total_destinos}</p>
      <p><strong>Reservas activas:</strong> ${data.reservas_activas}</p>
      <p><strong>Paquete más reservado:</strong> ${data.paquete_mas_reservado?.nombre || "No hay datos"}</p>
      <p><strong>Top usuarios:</strong></p>
      <ul>
        ${data.usuarios_destacados.map(u => `<li>${u.nombre} ${u.apellido} (${u.total_reservas} reservas)</li>`).join("")} 
      </ul>
    `; //se espera que sea un array de usuarios destacados. se crea una lista de <li> para cada usuario. une todos los ítems sin separadores y los inserta en el <ul>.
  } catch (err) {
    statsContainer.innerHTML = `<p>Error al cargar estadísticas: ${err.message}</p>`;
  }

  //redirecciona al adm segun el boton que haga click
  document.getElementById("btnUsuarios").addEventListener("click", () => {
    window.location.href = "crudUsuarios.html";
  });

  document.getElementById("btnClientes").addEventListener("click", () => {
    window.location.href = "crudClientes.html";
  });

  document.getElementById("btnServicios").addEventListener("click", () => {
    window.location.href = "crudServicios.html";
  });

  const reservasContainer = document.getElementById("reservasContainer");

  try {
    const resReservas = await fetch("http://localhost:8000/reservas/detalladas", {
      headers: { //hace un get a reservas detalladas
        "Authorization": `Bearer ${token}`
      }
    });

    if (!resReservas.ok) throw new Error("No se pudieron obtener las reservas");

    const reservas = await resReservas.json(); //Transforma la respuesta en un array de objetos con la información de las reservas.

    console.log(reservas);

    if (reservas.length === 0) {
      reservasContainer.innerHTML = "<p>No hay reservas registradas.</p>"; //Si no hay reservas, muestra un mensaje simple.
    } else { //Crea una tabla con encabezados para cliente, paquete, fecha y cantidad de personas. Usa .map() para recorrer el array de reservas y construir cada fila <tr>. Se accede a propiedades anidadas como r.usuario.nombre y r.paquete.nombre.
      reservasContainer.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Paquete</th>
              <th>Fecha</th>
              <th>Personas</th>
            </tr>
          </thead>
          <tbody>
            ${reservas.map(r => `
              <tr>
                <td>${r.usuario.nombre} ${r.usuario.apellido}</td>
                <td>${r.paquete.nombre}</td>
                <td>${r.fecha_reserva}</td>
                <td>${r.cantidad_personas}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    } //La función .join("") une todas las filas generadas en una sola cadena de texto (sin comas).
  } catch (err) {
    reservasContainer.innerHTML = `<p>Error al cargar reservas: ${err.message}</p>`;
  }


});