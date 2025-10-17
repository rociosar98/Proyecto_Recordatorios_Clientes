document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario")); //Toma el objeto usuario guardado como texto en sessionStorage y lo convierte a un objeto JavaScript con JSON.parse. Esto permite acceder luego a propiedades como usuario.nombre o usuario.apellido.

  const saludo = document.getElementById("adminSaludo");
  const statsContainer = document.getElementById("estadisticasContainer");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
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

  
});



