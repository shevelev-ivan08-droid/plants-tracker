document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const errorMsg = document.getElementById('error-msg');

    function showError(text) {
        errorMsg.textContent = text;
        errorMsg.classList.remove('hidden');
    }

    function handleAuth(response, redirectUrl) {
        if (response.ok) {
            window.location.href = '/';
        } else if (response.status === 422) {
            showError("Проверьте правильность введенных данных (длина логина/пароля).");
        } else if (response.status === 401 || response.status === 400) {
            response.json().then(data => showError(data.detail || "Ошибка входа"));
        } else {
            showError("Произошла ошибка сервера.");
        }
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMsg.classList.add('hidden');
            const data = {
                username: loginForm.username.value,
                password: loginForm.password.value
            };
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            handleAuth(res, '/');
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMsg.classList.add('hidden');
            const data = {
                username: registerForm.username.value,
                password: registerForm.password.value
            };
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            handleAuth(res, '/');
        });
    }
});