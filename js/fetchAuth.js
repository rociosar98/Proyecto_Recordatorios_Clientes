export async function fetchConAuth(url, options = {}) { //Exporta una función que recibe: url: la dirección del recurso al que se quiere acceder. options: un objeto opcional con configuración para el fetch (método, headers, body, etc.)
  const token = sessionStorage.getItem("token"); //Recupera el token JWT desde el sessionStorage

  if (!options.headers) options.headers = {}; //Si no existe options.headers, se crea uno vacío.
  options.headers.Authorization = `Bearer ${token}`; //Se agrega el token al encabezado Authorization, que es el estándar para tokens JWT.

  const response = await fetch(url, options); //Se hace la petición fetch real, con las opciones y el token incluidos.

  if (response.status === 401 || response.status === 403) {
    alert("Tu sesión expiró. Por favor iniciá sesión nuevamente.");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");
    window.location.href = "/login.html"; // Cambiá si tu login tiene otro nombre
    return; //Elimina el token y los datos del usuario del sessionStorage. Redirige a la página de login.
  }

  return response; //Si todo fue bien (no hubo error 401/403), retorna el objeto response para que el código que llama a fetchConAuth() pueda usarlo normalmente.
} //se fija si el token expiro y vuelve al login, y borra el usuario y el token