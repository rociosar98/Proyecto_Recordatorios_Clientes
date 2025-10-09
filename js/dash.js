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
    const sectionId = "section-" + btn.id.replace("btn", "").toLowerCase();
    const target = document.getElementById(sectionId);
    if (target) {
      target.classList.add("visible");
    } else {
      // Si no hay sección interna, redirigir a otra página (opcional)
      if (btn.id === "btnClientes") {
        window.location.href = "crudClientes.html";
      } else if (btn.id === "btnServicios") {
        window.location.href = "crudServicios.html";
      } else if (btn.id === "logout") {
        // Logout simple
        sessionStorage.clear();
        window.location.href = "login.html";
      }
    }
  });
});

// 🚀 Nuevo: Manejo dinámico de los botones CRUD
document.querySelectorAll("[data-action][data-module]").forEach(button => {
  button.addEventListener("click", () => {
    const accion = button.dataset.action;
    const modulo = button.dataset.module;

    // Aquí defines lo que quieres hacer según la acción y el módulo
    console.log(`Acción: ${accion} - Módulo: ${modulo}`);

    // Ejemplo: abrir un modal o redirigir
    switch (accion) {
      case "crear":
        if (modulo === "cliente") {
          window.location.href = "crudClientes.html";
        } else if (modulo === "servicio") {
          window.location.href = "crudServicios.html";
        } else {
          alert(`Crear ${modulo} aún no implementado`);
        }
        break;

      case "actualizar":
        alert(`Abrir formulario para ACTUALIZAR ${modulo}`);
        break;

      case "eliminar":
        alert(`Proceder a ELIMINAR ${modulo}`);
        break;

      case "ver":
        alert(`Mostrar lista de ${modulo}s`);
        break;

      default:
        console.warn("Acción desconocida");
    }
  });
});


