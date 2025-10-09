const BASE_URL = "http://localhost:8000";

export const authService = { //Está exportando un objeto llamado authService, para que pueda ser importado desde otros archivos (import { authService } from ...).
  login: async (email, password) => {
    try {
      const response = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }, //Informa al servidor que se está enviando datos en formato JSON.
        body: JSON.stringify({ email, password }) //Convierte el objeto con email y contraseña en un string JSON para enviarlo al servidor.
      });

      if (!response.ok) {
        throw new Error("Credenciales incorrectas");
      } //Si la respuesta no tiene código 200 (es decir, no fue exitosa), se lanza un error con el mensaje "Credenciales incorrectas". va directo al catch.

      const data = await response.json(); //Convierte la respuesta del servidor (que viene en formato JSON) en un objeto JavaScript llamado data.

      if (!data.accesoOk) {
        throw new Error("Acceso denegado por el backend");
      } // Verifica si el backend devolvió un campo accesoOk: true.
      // Si no, se lanza otro error manualmente con un mensaje más específico.

      
      sessionStorage.setItem("token", data.token); //Guarda el token de autenticación en el sessionStorage del navegador para mantener la sesión activa.
      sessionStorage.setItem("usuario", JSON.stringify(data.usuario)); // Guarda la información del usuario como un string JSON, también en sessionStorage.

      return data; //Devuelve los datos completos al lugar desde donde se llamó la función login.
    } catch (error) { // atrapa cualquier error que haya ocurrido dentro del try
      console.error("Error en login:", error.message); //Muestra un mensaje de error en la consola con el texto del error.
      throw error; //Vuelve a lanzar el error para que quien haya llamado a authService.login(...) también pueda manejarlo si quiere (por ejemplo, mostrar un mensaje al usuario).
    }
  }//
};
