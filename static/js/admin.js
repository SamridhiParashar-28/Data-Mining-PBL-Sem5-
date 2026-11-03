// Admin & Dataset Explorer Controller

document.addEventListener("DOMContentLoaded", async () => {
    await loadAdminStats();
});

async function loadAdminStats() {
    try {
        const data = await apiFetch("/api/admin/stats");
        if (!data) return;

        // Render Summary Counters
        const s = data.dataset_summary;
        document.getElementById("stat-total-samples").textContent = s.total_samples;
        document.getElementById("stat-features").textContent = s.total_features;
        document.getElementById("stat-avg-salary").textContent = formatCurrency(s.average_salary);
        document.getElementById("stat-promo-rate").textContent = `${s.overall_promotion_rate}%`;
        document.getElementById("stat-attr-rate").textContent = `${s.overall_attrition_rate}%`;
        document.getElementById("stat-users-count").textContent = data.registered_users_count;

        // Render Department Table
        const deptTbody = document.getElementById("admin-dept-tbody");
        if (deptTbody && data.department_analytics) {
            deptTbody.innerHTML = "";
            const d = data.department_analytics;
            Object.keys(d.counts).forEach(dept => {
                const tr = document.createElement("tr");
                tr.style.borderBottom = "1px solid var(--border-color)";
                tr.innerHTML = `
                    <td style="padding:0.6rem; font-weight:600;">${dept}</td>
                    <td style="padding:0.6rem;">${d.counts[dept]}</td>
                    <td style="padding:0.6rem;">${formatCurrency(d.average_salaries[dept] || 0)}</td>
                    <td style="padding:0.6rem;"><span class="badge badge-warning">${d.attrition_rates[dept]}%</span></td>
                    <td style="padding:0.6rem;"><span class="badge badge-success">${d.promotion_rates[dept]}%</span></td>
                `;
                deptTbody.appendChild(tr);
            });
        }

        // Render Registered Users Table
        const userTbody = document.getElementById("admin-users-tbody");
        if (userTbody && Array.isArray(data.registered_users)) {
            userTbody.innerHTML = "";
            data.registered_users.forEach(u => {
                const tr = document.createElement("tr");
                tr.style.borderBottom = "1px solid var(--border-color)";
                tr.innerHTML = `
                    <td style="padding:0.6rem; font-weight:600;">${u.employee_id || 'N/A'}</td>
                    <td style="padding:0.6rem;">${u.name}</td>
                    <td style="padding:0.6rem; color:var(--text-secondary);">${u.email}</td>
                    <td style="padding:0.6rem;"><span class="badge badge-primary">${u.department || 'Engineering'}</span></td>
                    <td style="padding:0.6rem;"><span class="badge badge-success">${u.role || 'employee'}</span></td>
                    <td style="padding:0.6rem; font-size:0.75rem; color:var(--text-muted);">${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Recent'}</td>
                `;
                userTbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Failed to load admin stats", err);
    }
}

