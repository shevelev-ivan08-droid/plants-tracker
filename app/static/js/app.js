const listContainer = document.getElementById('plant-list');
const loadingEl = document.getElementById('loading');
const emptyStateEl = document.getElementById('empty-state');
const errorEl = document.getElementById('global-error');
const usernameEl = document.getElementById('current-username');
const searchInput = document.getElementById('search-input');
const filterFavorite = document.getElementById('filter-favorite');
const sortSelect = document.getElementById('sort-select');
const addForm = document.getElementById('add-plant-form');

let currentPlants = [];

async function checkAuth() {
    const res = await fetch('/api/auth/me');
    if (res.status === 401) {
        window.location.href = '/login';
        return false;
    }
    const user = await res.json();
    usernameEl.textContent = user.username;
    return true;
}

async function loadPlants() {
    loadingEl.classList.remove('hidden');
    emptyStateEl.classList.add('hidden');
    errorEl.classList.add('hidden');
    listContainer.innerHTML = ''; // Очистка (безопасно, так как мы только удаляем)

    const params = new URLSearchParams();
    if (searchInput.value) params.append('search', searchInput.value);
    if (filterFavorite.value) params.append('is_favorite', filterFavorite.value);
    if (sortSelect.value) params.append('sort', sortSelect.value);

    try {
        const res = await fetch(`/api/plants?${params.toString()}`);
        if (res.status === 401) { window.location.href = '/login'; return; }
        if (!res.ok) throw new Error("Ошибка загрузки");
        
        currentPlants = await res.json();
        renderPlants();
    } catch (e) {
        errorEl.textContent = e.message;
        errorEl.classList.remove('hidden');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

function renderPlants() {
    listContainer.innerHTML = '';
    if (currentPlants.length === 0) {
        emptyStateEl.classList.remove('hidden');
        return;
    }
    emptyStateEl.classList.add('hidden');

    currentPlants.forEach(plant => {
        const card = document.createElement('div');
        card.className = 'plant-card';

        const title = document.createElement('h3');
        title.textContent = plant.name; // Безопасный вывод
        if (plant.is_favorite) title.textContent += ' ⭐';

        const meta = document.createElement('div');
        meta.className = 'plant-meta';
        meta.textContent = `Вид: ${plant.species || 'Не указан'} | Полив: каждые ${plant.watering_interval_days} дн. | Последний: ${plant.last_watered_at || 'никогда'}`;

        const actions = document.createElement('div');
        actions.className = 'plant-actions';

        const waterBtn = document.createElement('button');
        waterBtn.className = 'btn';
        waterBtn.textContent = 'Полить сегодня';
        waterBtn.onclick = () => waterPlant(plant.id);

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.textContent = 'Удалить';
        deleteBtn.onclick = () => deletePlant(plant.id);

        actions.append(waterBtn, deleteBtn);
        card.append(title, meta, actions);
        listContainer.append(card);
    });
}

async function waterPlant(id) {
    const today = new Date().toISOString().split('T')[0];
    const res = await fetch(`/api/plants/${id}/waterings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ watered_at: today })
    });
    if (res.ok) loadPlants();
    else alert("Ошибка при поливе");
}

async function deletePlant(id) {
    if (!confirm("Удалить это растение?")) return;
    const res = await fetch(`/api/plants/${id}`, { method: 'DELETE' });
    if (res.ok || res.status === 204) loadPlants();
    else alert("Ошибка удаления");
}

// Обработчики
addForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: addForm.name.value,
        species: addForm.species.value || null,
        watering_interval_days: parseInt(addForm.watering_interval_days.value)
    };
    const res = await fetch('/api/plants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (res.ok) {
        addForm.reset();
        loadPlants();
    } else {
        alert("Ошибка добавления растения (проверьте поля)");
    }
});

document.getElementById('logout-btn').addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
});

let searchTimeout;
searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(loadPlants, 300); // Дебаунс
});
filterFavorite.addEventListener('change', loadPlants);
sortSelect.addEventListener('change', loadPlants);

// Инициализация
(async () => {
    if (await checkAuth()) {
        loadPlants();
    }
})();