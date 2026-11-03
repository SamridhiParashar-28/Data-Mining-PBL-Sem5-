// Global Common Utilities

// --- Theme Management ---
function initTheme() {
    const savedTheme = localStorage.getItem("app_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("app_theme", next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById("theme-toggle-btn");
    if (btn) {
        btn.innerHTML = theme === "dark" ? "☀️" : "🌙";
        btn.setAttribute("title", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
    }
}

// --- Auth Token Management ---
function getToken() {
    return localStorage.getItem("jwt_token") || null;
}

function setToken(token) {
    localStorage.setItem("jwt_token", token);
}

function getUser() {
    try {
        const u = localStorage.getItem("current_user");
        return u ? JSON.parse(u) : null;
    } catch {
        return null;
    }
}

function setUser(user) {
    localStorage.setItem("current_user", JSON.stringify(user));
}

function logout() {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("current_user");
    fetch("/api/auth/signout", { method: "POST" }).finally(() => {
        window.location.href = "/signin";
    });
}

// --- API Client ---
async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(endpoint, {
            ...options,
            headers
        });

        if (response.status === 401 && !endpoint.includes("/api/auth/")) {
            // Unauthorized -> redirect to signin
            showToast("Session expired. Please sign in again.", "warning");
            setTimeout(() => { window.location.href = "/signin"; }, 1000);
            return null;
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || "An error occurred.");
        }
        return data;
    } catch (err) {
        showToast(err.message || "Network error. Please try again.", "error");
        throw err;
    }
}

// --- Toast Notifications ---
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "⚠️";
    if (type === "warning") icon = "🔔";

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// --- Formatters ---
function formatCurrency(val) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
}

function formatPct(val) {
    return `${(val).toFixed(1)}%`;
}

// Initialize theme on script load
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    const themeBtn = document.getElementById("theme-toggle-btn");
    if (themeBtn) {
        themeBtn.addEventListener("click", toggleTheme);
    }
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }
});

