import { authService } from "./authService.js";

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const loginError = document.getElementById("loginError");
  const container = document.querySelector(".login-container");

  const token = sessionStorage.getItem("token"); //Revisa si hay un token guardado en el sessionStorage, lo que indicaría que el usuario ya está logueado.
  const usuario = JSON.parse(sessionStorage.getItem("usuario") || "{}"); //Los datos del usuario (usuario), que están guardados como JSON. Si no existe, se usa un objeto vacío {} por defecto para evitar errores.

  if (token) {

    fetch("http://localhost:8000/usuarios", {
      headers: { Authorization: `Bearer ${token}` } //Se envía el token como header de autorización con formato Bearer.
    })
      .then(res => {
        if (!res.ok) throw new Error("Token expirado"); //Si la respuesta del servidor no es exitosa (res.ok es false), se lanza un error manualmente que será capturado en el .catch.
        
        container.innerHTML = `<h2>Sesión activa</h2><p>Redirigiendo...</p>`; //Si el token es válido, reemplaza el contenido del login con un mensaje que avisa que ya hay una sesión iniciada.
        const rol = usuario.rol?.toLowerCase(); //Toma el rol del usuario (por ejemplo, "Admin" o "Usuario") y lo convierte a minúsculas para compararlo de forma segura. El ?. es encadenamiento opcional, por si el objeto no tiene esa propiedad.
        const destino = rol === "admin" ? "dashboard.html" : "destinos.html"; //Según el rol del usuario, define a qué página debe redirigirse: Si es "admin" → lo manda al dashboard de administración. Si no lo manda a la página de destinos normales.
        setTimeout(() => (window.location.href = destino), 1000); //Después de 1 segundo (1000 ms), redirige automáticamente al usuario a la página correspondiente.
      })
      .catch(err => {
        
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("usuario");
        console.warn("Token inválido o expirado. Sesión limpia.");
      }); //Si hubo un error en la validación del token (por ejemplo, expirado), borra los datos del usuario y el token del sessionStorage, y muestra un mensaje de advertencia en consola.

    return;
}


  loginForm.addEventListener("submit", async (e) => { //Agrega un manejador de evento para el envío del formulario. Se marca como async porque se hará una llamada asíncrona al backend para autenticar.
    e.preventDefault(); //Previene el comportamiento por defecto del formulario (recargar la página).
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const response = await authService.login(email, password); //Llama a la función login del authService, enviando el email y contraseña. await espera la respuesta del servidor.
      console.log("Respuesta del backend:", response);

      sessionStorage.setItem("token", response.token); //Guarda el token en sessionStorage para mantener la sesión activa.
      sessionStorage.setItem("usuario", JSON.stringify(response.usuario)); //Guarda los datos del usuario, convirtiéndolos a texto con JSON.stringify.
      console.log("Usuario guardado en sessionStorage:", response.usuario);

      alert(`¡Bienvenido ${response.usuario.nombre} ${response.usuario.apellido}!`);

      const rol = response.usuario.rol.toLowerCase(); //Extrae el rol del usuario y lo convierte a minúsculas, para facilitar la comparación.

      console.log(rol)

      if (rol === "admin") { //Redirige al usuario a diferentes páginas dependiendo de su rol:
        window.location.href = "dashboard.html";
      } else {
        window.location.href = "destinos.html";
      }

    } catch (err) {
      alert("Error de autenticación: " + err.message); //Si hay algún error (por ejemplo, usuario o contraseña incorrectos), se muestra un mensaje con el error.
    }
  });
});