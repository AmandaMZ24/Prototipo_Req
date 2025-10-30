const API_URL = "http://127.0.0.1:5000/pets/";
const token = localStorage.getItem("token");
if (!token) {
  alert("Debes iniciar sesión");
  window.location.href = "login.html";
}

function getUserRole() {
  try {
    const payloadBase64 = token.split('.')[1];
    const decoded = JSON.parse(atob(payloadBase64));
    return decoded.role || (decoded.identity && decoded.identity.role) || null;
  } catch (err) {
    console.error("Error al decodificar token:", err);
    return null;
  }
}

function renderNavbar() {
  const navbar = document.getElementById("navbar");
  const role = getUserRole();
  let links = `<a href="index.html">Inicio</a> | <a href="#" id="btn-logout">Cerrar sesión</a>`;
  if (role === "admin") {
    links = `
      <a href="index.html">Inicio</a> |
      <a href="add_pet.html">Agregar mascota</a> |
      <a href="admin_stats.html">Ver estadísticas</a> |
      <a href="admin_requests.html">Ver solicitudes de adopción</a> |
      <a href="#" id="btn-logout">Cerrar sesión</a>
    `;
  }
  navbar.innerHTML = links;
  const btn = document.getElementById("btn-logout");
  if (btn) {
    btn.addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = "index.html";
    });
  }
}

async function loadPets(filters = {}) {
  let url = API_URL;
  const res = await fetch(url);
  const pets = await res.json();
  const list = document.getElementById("pet-list");
  const role = getUserRole();
  list.innerHTML = "";

  const filtered = pets.filter(p => {
    const speciesMatch = filters.species ? p.species === filters.species : true;
    const availMatch = filters.availability ? p.availability === filters.availability : true;
    return speciesMatch && availMatch;
  });

  filtered.forEach(p => {
    const div = document.createElement("div");
    div.className = "pet-card";
    div.innerHTML = `
      <img src="${p.photo_url}" width="150" height="150" style="object-fit:cover"><br>
      <h3>${p.name}</h3>
      <p>${p.species} - ${p.breed}</p>
      <p>Edad: ${p.age} años</p>
      <p>Estado: ${p.availability}</p>
      ${role === "admin" ? `
        <button onclick="editPet(${p.id})">✏️ Editar</button>
        <button onclick="deletePet(${p.id})">🗑️ Eliminar</button>
      ` : ""}    
    `;

    if (role === "adoptante") {
      // Evitar colapsar/expandir cuando el click viene de un control interactivo (textarea/button/input...)
      div.addEventListener("click", (ev) => {
        const tag = ev.target.tagName;
        const interactive = ["TEXTAREA", "BUTTON", "INPUT", "SELECT", "A", "LABEL"];
        if (interactive.includes(tag)) return;
        expandCard(div, p);
      });
    }
    list.appendChild(div);
  });
}

function expandCard(div, pet) {
  // Si ya está expandida, la colapsa
  if (div.classList.contains("expanded")) {
    div.classList.remove("expanded");
    div.innerHTML = `
      <img src="${pet.photo_url}" width="150" height="150" style="object-fit:cover"><br>
      <h3>${pet.name}</h3>
      <p>${pet.species} - ${pet.breed}</p>
      <p>Edad: ${pet.age} años</p>
      <p>Estado: ${pet.availability}</p>
    `;
    return;
  }

  div.classList.add("expanded");
  div.innerHTML = `
    <img src="${pet.photo_url}" width="180" height="180" style="object-fit:cover"><br>
    <h3>${pet.name}</h3>
    <p><strong>Especie:</strong> ${pet.species}</p>
    <p><strong>Raza:</strong> ${pet.breed}</p>
    <p><strong>Sexo:</strong> ${pet.sex || "No especificado"}</p>
    <p><strong>Estado de salud:</strong> ${pet.health_status}</p>
    <p><strong>Disponibilidad:</strong> ${pet.availability}</p>
    <textarea id="reason-${pet.id}" placeholder="¿Por qué quieres adoptar a ${pet.name}?"></textarea><br>
    <button id="send-${pet.id}">💌 Enviar solicitud</button>
  `;

  // Evitar que clics en elementos internos cierren la tarjeta
  div.querySelector("textarea").addEventListener("click", e => e.stopPropagation());
  div.querySelector("button").addEventListener("click", e => e.stopPropagation());
  div.querySelector("button").addEventListener("click", () => sendAdoption(pet.id));
}

async function sendAdoption(petId) {
  const reason = document.getElementById(`reason-${petId}`).value.trim();

  if (!reason) {
    alert("Por favor escribe un motivo para tu solicitud.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/requests", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ pet_id: petId, reason })
    });

    // Si la respuesta no es correcta, mostrar error con detalles
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.msg || `Error ${res.status}: No se pudo enviar la solicitud`);
    }

    const data = await res.json();
    alert(data.msg || "Solicitud enviada con éxito 🐾");
  } catch (err) {
    console.error("Error al enviar la solicitud:", err);
    alert(err.message);
  }
}

function editPet(id) {
  window.location.href = `edit_pet.html?id=${id}`;
}

async function deletePet(id) {
  if (!confirm("¿Eliminar esta mascota?")) return;
  await fetch(`${API_URL}${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });
  loadPets();
}

renderNavbar();

document.addEventListener("DOMContentLoaded", () => {
  const btnFilter = document.getElementById("btn-filter");
  btnFilter.addEventListener("click", () => {
    const species = document.getElementById("filter-species").value;
    const availability = document.getElementById("filter-availability").value;
    loadPets({ species, availability });
  });
  loadPets();
});
