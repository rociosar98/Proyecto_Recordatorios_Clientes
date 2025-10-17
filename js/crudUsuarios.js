import {fetchConAuth} from "./fetchAuth.js";

document.addEventListener("DOMContentLoaded", async () => {
    const token = sessionStorage.getItem("token");
    const usuario = JSON.parse(sessionStorage.getItem("usuario"));
    const saludo = document.getElementById("adminSaludo");

    if (usuario) {
    saludo.textContent = `Hola admin ${usuario.nombre} ${usuario.apellido} 👋`;
    }

    const form = document.getElementById("crudForm");
    const tabla = document.getElementById("usuariosTabla");

    // Listar usuarios
    async function cargarUsuarios() {
    try {
        const res = await fetchConAuth("http://localhost:8000/usuarios");

        if (!res.ok) throw new Error("No se pudieron obtener los usuarios");
        const data = await res.json();

        tabla.innerHTML = "";
        data.forEach(u => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <td>${u.nombre}</td>
            <td>${u.apellido}</td>
            <td>${u.correo}</td>
            <td>${u.rol}</td>
            <td>${u.permiso}</td>
            `;
            tr.dataset.id = u.id;
            tr.dataset.nombre = u.nombre;
            tr.dataset.apellido = u.apellido;
            tr.dataset.correo = u.correo;
            tr.dataset.rol = u.rol;
            tr.dataset.permiso = u.permiso;

          tr.addEventListener("click", () => {

              document.getElementById("usuarioId").value = u.id;
              document.getElementById("nombre").value = u.nombre;
              document.getElementById("apellido").value = u.apellido;
              document.getElementById("correo").value = u.correo;
              document.getElementById("rol").value = u.rol;
              document.getElementById("permiso").value = u.permiso;

              form.querySelector("button[type='submit']").style.display = "none";
              btnActualizar.style.display = "inline-block";
              btnEliminar.style.display = "inline-block";
          });

          tabla.appendChild(tr);

        });
      } catch (err) {
        alert("Error al cargar los usuarios: " + err.message);
      }
}


      await cargarUsuarios();

      form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nuevoUsuario = {
          nombre: document.getElementById("nombre").value,
          apellido: document.getElementById("apellido").value,
          correo: document.getElementById("correo").value,
          password: document.getElementById("password").value,
          rol: document.getElementById("rol").value,
          permiso: document.getElementById("permiso").value,
          activo: true
        };

        console.log(nuevoUsuario)

        try {
          const res = await fetch("http://localhost:8000/usuarios", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(nuevoUsuario)
          });

          if (!res.ok) {
            const errorData = await res.json();
            console.error("Error detalle:", errorData);
            throw new Error("Error al crear el usuario");
        }

          alert("Usuario creado correctamente");
          form.reset();
          await cargarUsuarios();
        } catch (err) {
          alert("Error: " + err.message);
        }
      });

      
      
    const btnActualizar = document.getElementById("btnActualizar");
    const btnEliminar = document.getElementById("btnEliminar");

    // ACTUALIZAR USUARIO
    btnActualizar.addEventListener("click", async () => {
      const id = document.getElementById("usuarioId").value;
      console.log("ID a actualizar:", id);

      if (!id) {
        alert("Seleccioná un usuario antes de actualizar");
        return;
    }

      const passwordValue = document.getElementById("password").value;

      const usuarioActualizado = {
        nombre: document.getElementById("nombre").value,
        apellido: document.getElementById("apellido").value,
        correo: document.getElementById("correo").value,
        password: document.getElementById("password").value,
        rol: document.getElementById("rol").value,
        permiso: document.getElementById("permiso").value,
        activo: true
      };

      if(passwordValue.trim() !== "") {
        usuarioActualizado.password = passwordValue;
      }

      console.log("Payload actualización:", usuarioActualizado);

      try {
        const res = await fetch(`http://localhost:8000/usuarios/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(usuarioActualizado)
        });

        const data = await res.json();
        console.log("Respuesta del servidor:", res.status, data);

        if (!res.ok) {
      // Mostrar detalle de error
            const detalle = data.detail || data;
            alert("Error al actualizar el usuario: " + JSON.stringify(detalle));
            return;
        }

        alert("Usuario actualizado");
        form.reset();
        btnActualizar.style.display = "none";
        btnEliminar.style.display = "none";
        form.querySelector("button[type='submit']").style.display = "inline-block";
        await cargarUsuarios();
      } catch (err) {
        alert("Error: " + err.message);
      }
    });

    btnEliminar.addEventListener("click", async () => {
      const id = document.getElementById("usuarioId").value;
      if (!confirm("¿Seguro que querés eliminar este usuario?")) return;

        try {
        const res = await fetch(`http://localhost:8000/usuarios/${id}`, {
            method: "DELETE",
            headers: {
            Authorization: `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Error al eliminar el usuario");

        alert("Usuario eliminado");
        form.reset();
        btnActualizar.style.display = "none";
        btnEliminar.style.display = "none";
        form.querySelector("button[type='submit']").style.display = "inline-block";
        await cargarUsuarios();
        } catch (err) {
        alert("Error: " + err.message);
        }
    });

    });