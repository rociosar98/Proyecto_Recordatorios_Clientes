document.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");
  const usuario = JSON.parse(sessionStorage.getItem("usuario"));

  const saludo = document.getElementById("adminSaludo");

  if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
  }

  try {
    const res = await fetch("http://localhost:8000/dashboard/admin", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

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
