// Asociar botones con secciones
const buttons = document.querySelectorAll(".sidebar button");
const sections = document.querySelectorAll(".main-content .section");

buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    // Sacar clase "active" de todos los botones
    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // Ocultar todas las secciones
    sections.forEach(sec => sec.classList.remove("visible"));

    // Mostrar sección correspondiente
    let sectionId;
    if (btn.id === "configuracion") {
      sectionId = "section-configuracion";
    } else {
      sectionId = "section-" + btn.id.replace("btn", "").toLowerCase();
    }
    
    const target = document.getElementById(sectionId);
    if (target) {
      target.classList.add("visible");
    } else {
      // Si no hay sección interna, redirigir a otra página (opcional)
      // Redirecciones a otras páginas
      if (btn.id == "btnUsuarios") {
        window.location.href = "crudUsuarios.html"
      } else if (btn.id === "btnClientes") {
        window.location.href = "crudClientes.html";
      } else if (btn.id === "btnServicios") {
        window.location.href = "crudServicios.html";
      } else if (btn.id === "btnAsignarServicio") {
        window.location.href = "asignar_servicio.html";
      } else if (btn.id === "btnHistorial") {
        window.location.href = "historial.html";
      } else if (btn.id === "btnListado") {
        window.location.href = "listadoMensual.html";
      } else if (btn.id === "btnFacturacion") {
        window.location.href = "pagos.html";
      } else if (btn.id === "logout") {
        // Logout simple
        sessionStorage.clear();
        window.location.href = "index.html";
      }
    }
  });
});


// FORMULARIO CONFIGURACIÓN EMPRESA
const configForm = document.getElementById("configForm");

// Cargar datos existentes al iniciar
window.addEventListener("DOMContentLoaded", async () => {
  const token = sessionStorage.getItem("token");

  try {
    const response = await fetch("http://localhost:8000/empresa", {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (response.ok) {
      const datos = await response.json();

      document.getElementById("cbu").value = datos.cbu || "";
      document.getElementById("cvu").value = datos.cvu || "";

      const formasPagoArray = (datos.formas_pago || "")
        .split(",")
        .map(f => f.trim());

      document.querySelectorAll("#formasPago input[type=checkbox]").forEach(cb => {
        cb.checked = formasPagoArray.includes(cb.value);
      });
    } else {
      console.warn("No se pudieron cargar los datos de la empresa (status)", response.status);
    }
  } catch (error) {
    console.error("❌ Error al obtener los datos de la empresa:", error);
  }
});

// Guardar configuración
configForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const cbu = document.getElementById("cbu").value.trim();
  const cvu = document.getElementById("cvu").value.trim();
  const formasPago = Array.from(
    document.querySelectorAll("#formasPago input[type=checkbox]:checked")
  )
    .map(cb => cb.value)
    .join(", ");

  const datos = { cbu, cvu, formas_pago: formasPago };
  const token = sessionStorage.getItem("token");

  if (!token) {
    alert("⚠️ No hay token de sesión. Iniciá sesión como admin nuevamente.");
    window.location.href = "index.html";
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/empresa", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(datos),
    });

    if (!response.ok) {
      if (response.status === 401) {
        alert("⚠️ Sesión expirada o no autorizada. Iniciá sesión nuevamente.");
        sessionStorage.clear();
        window.location.href = "index.html";
        return;
      }

      const errText = await response.text();
      throw new Error(`Error al guardar (status ${response.status}): ${errText}`);
    }

    const result = await response.json();
    console.log("✅ Datos guardados:", result);
    alert("✅ Datos de la empresa guardados correctamente!");
  } catch (error) {
    alert("❌ Error al guardar: " + error.message);
    console.error(error);
  }
});

