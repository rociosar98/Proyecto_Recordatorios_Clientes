const BASE_URL = "http://localhost:8000";

export const authService = {
  login: async (email, password) => {
    try {
      const response = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error("Credenciales incorrectas");
      }

      const data = await response.json();

      if (!data.accesoOk) {
        throw new Error("Acceso denegado por el backend");
      }

      sessionStorage.setItem("token", data.token);
      sessionStorage.setItem("usuario", JSON.stringify(data.usuario));

      return data;
    } catch (error) {
      console.error("Error en login:", error.message);
      throw error;
    }
  }
};
