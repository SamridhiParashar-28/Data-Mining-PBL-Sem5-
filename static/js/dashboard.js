// Employee Dashboard Controller

let currentProfile = {};
let presets = [];

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Verify Authentication & Load Profile
    await loadUserProfile();

    // 2. Load Preset Profiles
    await loadPresets();

    // 3. Form Submit Listener
    const profileForm = document.getElementById("profile-form");
    if (profileForm) {
        profileForm.addEventListener("submit", handleProfileSave);
    }

    // 4. Attach Analysis Event Listeners
    setupAnalysisTriggers();

    // 5. Preset Selector
    const presetSelect = document.getElementById("preset-select");
    if (presetSelect) {
        presetSelect.addEventListener("change", handlePresetSelection);
    }

    // 6. Export Report Listener
    const exportBtn = document.getElementById("export-report-btn");
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            window.location.href = "/api/analysis/export-csv";
        });
    }

    // 7. Print Report Listener
    const printBtn = document.getElementById("print-report-btn");
    if (printBtn) {
        printBtn.addEventListener("click", () => window.print());
    }
});

async function loadUserProfile() {
    try {
        const res = await apiFetch("/api/auth/me");
        if (!res || !res.user) return;

        const user = res.user;
        setUser(user);

        // Update Greetings & Header
        document.getElementById("user-name-display").textContent = user.name;
        document.getElementById("user-id-display").textContent = user.employee_id || "EMP-USER";
        document.getElementById("user-dept-display").textContent = user.department || "Engineering";

        const hour = new Date().getHours();
        let greeting = "Good evening";
        if (hour < 12) greeting = "Good morning";
        else if (hour < 18) greeting = "Good afternoon";
        document.getElementById("dashboard-greeting").textContent = `${greeting}, ${user.name.split(' ')[0]}!`;

        // Load Employee Profile
        if (res.profile) {
            currentProfile = res.profile;
            populateForm(res.profile);
        }
    } catch (err) {
        console.error("Profile load error:", err);
    }
}

function populateForm(p) {
    const fields = [
        "age", "department", "job_role", "education_level", "education_field",
        "monthly_income", "years_at_company", "years_in_current_role",
        "years_since_last_promotion", "total_working_years", "performance_rating",
        "projects_completed", "training_hours_last_year", "overtime",
        "job_satisfaction", "work_life_balance", "environment_satisfaction",
        "distance_from_home", "stock_option_level"
    ];

    fields.forEach(field => {
        const el = document.getElementById(`input-${field}`);
        if (el && p[field] !== undefined) {
            el.value = p[field];
        }
    });
}

function getFormData() {
    return {
        age: parseInt(document.getElementById("input-age").value) || 30,
        department: document.getElementById("input-department").value,
        job_role: document.getElementById("input-job_role").value,
        education_level: parseInt(document.getElementById("input-education_level").value) || 3,
        education_field: document.getElementById("input-education_field").value,
        monthly_income: parseFloat(document.getElementById("input-monthly_income").value) || 6500.0,
        years_at_company: parseInt(document.getElementById("input-years_at_company").value) || 3,
        years_in_current_role: parseInt(document.getElementById("input-years_in_current_role").value) || 2,
        years_since_last_promotion: parseInt(document.getElementById("input-years_since_last_promotion").value) || 1,
        total_working_years: parseInt(document.getElementById("input-total_working_years").value) || 6,
        performance_rating: parseInt(document.getElementById("input-performance_rating").value) || 4,
        projects_completed: parseInt(document.getElementById("input-projects_completed").value) || 7,
        training_hours_last_year: parseInt(document.getElementById("input-training_hours_last_year").value) || 30,
        overtime: document.getElementById("input-overtime").value,
        job_satisfaction: parseInt(document.getElementById("input-job_satisfaction").value) || 4,
        work_life_balance: parseInt(document.getElementById("input-work_life_balance").value) || 3,
        environment_satisfaction: parseInt(document.getElementById("input-environment_satisfaction").value) || 4,
        distance_from_home: parseInt(document.getElementById("input-distance_from_home").value) || 10,
        stock_option_level: parseInt(document.getElementById("input-stock_option_level").value) || 1
    };
}

async function handleProfileSave(e) {
    e.preventDefault();
    const btn = document.getElementById("save-profile-btn");
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "<span>Saving Profile...</span>";

    const payload = getFormData();
    try {
        const res = await apiFetch("/api/employee/profile", {
            method: "POST",
            body: JSON.stringify(payload)
        });
        if (res && res.success) {
            currentProfile = payload;
            showToast("Profile data updated successfully!", "success");
        }
    } catch (err) {
        // Handled by toast
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function loadPresets() {
    try {
        presets = await apiFetch("/api/employee/presets");
        const select = document.getElementById("preset-select");
        if (select && Array.isArray(presets)) {
            presets.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = `${p.title} (${p.badge})`;
                select.appendChild(opt);
            });
        }
    } catch (err) {
        console.error("Failed to load presets", err);
    }
}

function handlePresetSelection(e) {
    const selectedId = e.target.value;
    if (!selectedId) return;
    const found = presets.find(p => p.id === selectedId);
    if (found && found.data) {
        populateForm(found.data);
        showToast(`Loaded preset profile: ${found.title}`, "info");
    }
}

function setupAnalysisTriggers() {
    const triggerButtons = document.querySelectorAll("[data-analysis-type]");
    triggerButtons.forEach(btn => {
        btn.addEventListener("click", async () => {
            const analysisType = btn.getAttribute("data-analysis-type");
            await runAnalysis(analysisType);
        });
    });

    const runAllBtn = document.getElementById("run-all-analysis-btn");
    if (runAllBtn) {
        runAllBtn.addEventListener("click", async () => {
            await runAnalysis("all");
        });
    }
}

async function runAnalysis(type) {
    const resultsContainer = document.getElementById("results-section");
    resultsContainer.style.display = "block";
    resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });

    // Show loading skeleton
    document.getElementById("results-loading").style.display = "block";
    document.getElementById("results-content").style.display = "none";

    const currentData = getFormData();

    try {
        const res = await apiFetch("/api/analysis/run", {
            method: "POST",
            body: JSON.stringify({
                analysis_type: type,
                profile_data: currentData
            })
        });

        if (res && res.results) {
            renderAnalysisResults(res.results);
            showToast("Data mining pipeline analysis completed!", "success");
        }
    } catch (err) {
        console.error("Analysis execution error", err);
    } finally {
        document.getElementById("results-loading").style.display = "none";
        document.getElementById("results-content").style.display = "block";
    }
}

function renderAnalysisResults(results) {
    const container = document.getElementById("results-cards-grid");
    container.innerHTML = "";

    // 1. Promotion Card
    if (results.promotion) {
        const p = results.promotion;
        const card = document.createElement("div");
        card.className = "card";
        const isHigh = p.probability >= 0.5;
        const color = isHigh ? "var(--success)" : "var(--info)";

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="badge ${isHigh ? 'badge-success' : 'badge-primary'}">Promotion Probability Analysis</span>
                <span style="font-size:0.8rem; color:var(--text-muted)">Confidence: ${p.confidence_pct}%</span>
            </div>
            <div style="display:flex; align-items:center; gap:1.5rem; margin-bottom:1.25rem;">
                <div style="font-size:2.8rem; font-weight:800; color:${color}; line-height:1;">
                    ${p.probability_pct}%
                </div>
                <div>
                    <h3 style="font-size:1.15rem; margin-bottom:0.25rem;">${p.prediction}</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">Model: ${p.pipeline_used}</p>
                </div>
            </div>
            <div style="margin-bottom:1rem;">
                <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-secondary); margin-bottom:0.5rem;">Positive Catalysts:</h4>
                <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
                    ${p.positive_factors.length ? p.positive_factors.map(f => `<span class="badge badge-success">+ ${f.factor}</span>`).join('') : '<span style="font-size:0.85rem; color:var(--text-muted);">None identified</span>'}
                </div>
            </div>
            ${p.negative_factors.length ? `
            <div style="margin-bottom:1rem;">
                <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-secondary); margin-bottom:0.5rem;">Improvement Areas:</h4>
                <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
                    ${p.negative_factors.map(f => `<span class="badge badge-warning">⚠ ${f.factor}</span>`).join('')}
                </div>
            </div>` : ''}
            <div style="background:var(--bg-input); padding:0.85rem; border-radius:var(--radius-md); font-size:0.85rem;">
                <strong>Strategic Recommendations:</strong>
                <ul style="margin-left:1.2rem; margin-top:0.35rem; color:var(--text-secondary);">
                    ${p.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(card);
    }

    // 2. Attrition / Job Change Risk Card
    if (results.attrition) {
        const a = results.attrition;
        const card = document.createElement("div");
        card.className = "card";
        let badgeClass = "badge-success";
        let color = "var(--success)";
        if (a.attrition_probability >= 0.5) {
            badgeClass = "badge-danger";
            color = "var(--danger)";
        } else if (a.attrition_probability >= 0.25) {
            badgeClass = "badge-warning";
            color = "var(--warning)";
        }

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="badge ${badgeClass}">Attrition & Flight Risk Analysis</span>
                <span style="font-size:0.8rem; color:var(--text-muted)">Confidence: ${a.confidence_pct}%</span>
            </div>
            <div style="display:flex; align-items:center; gap:1.5rem; margin-bottom:1.25rem;">
                <div style="font-size:2.8rem; font-weight:800; color:${color}; line-height:1;">
                    ${a.attrition_pct}%
                </div>
                <div>
                    <h3 style="font-size:1.15rem; margin-bottom:0.25rem;">${a.risk_tier}</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">Predicted probability of departure</p>
                </div>
            </div>
            ${a.risk_drivers.length ? `
            <div style="margin-bottom:1rem;">
                <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-secondary); margin-bottom:0.5rem;">Detected Risk Drivers:</h4>
                <div style="display:flex; flex-direction:column; gap:0.4rem;">
                    ${a.risk_drivers.map(d => `
                        <div style="font-size:0.85rem; background:rgba(239, 68, 68, 0.1); border-left:3px solid var(--danger); padding:0.4rem 0.6rem; border-radius:4px;">
                            <strong>${d.driver}</strong> (${d.severity} Impact): <span style="color:var(--text-secondary);">${d.note}</span>
                        </div>
                    `).join('')}
                </div>
            </div>` : '<div style="margin-bottom:1rem; font-size:0.85rem; color:var(--success);">✓ No major flight risks identified in current profile.</div>'}
            <div style="background:var(--bg-input); padding:0.85rem; border-radius:var(--radius-md); font-size:0.85rem;">
                <strong>Retention & Engagement Plan:</strong>
                <ul style="margin-left:1.2rem; margin-top:0.35rem; color:var(--text-secondary);">
                    ${a.retention_actions.map(act => `<li>${act}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(card);
    }

    // 3. Performance Score Card
    if (results.performance) {
        const perf = results.performance;
        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="badge badge-primary">Performance Score & Department Ranking</span>
                <span class="badge badge-success">${perf.badge}</span>
            </div>
            <div style="display:flex; align-items:center; gap:1.5rem; margin-bottom:1.25rem;">
                <div style="font-size:2.8rem; font-weight:800; color:var(--accent); line-height:1;">
                    ${perf.composite_score} <span style="font-size:1.1rem; color:var(--text-muted);">/100</span>
                </div>
                <div>
                    <h3 style="font-size:1.15rem; margin-bottom:0.25rem;">${perf.performance_band}</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">Top ${100 - perf.percentile < 1 ? '1%' : `${(100 - perf.percentile).toFixed(0)}%`} of departmental peers</p>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:0.75rem; margin-bottom:1rem;">
                ${perf.metrics_breakdown.map(m => `
                    <div style="background:var(--bg-input); padding:0.6rem; border-radius:var(--radius-sm); text-align:center;">
                        <div style="font-size:0.75rem; color:var(--text-muted);">${m.metric}</div>
                        <div style="font-weight:700; font-size:1rem; margin:0.2rem 0;">${m.score}</div>
                        <span class="badge ${m.status === 'Strong' ? 'badge-success' : 'badge-warning'}" style="font-size:0.7rem;">${m.status}</span>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(card);
    }

    // 4. Compensation Fairness Card
    if (results.compensation) {
        const c = results.compensation;
        const card = document.createElement("div");
        card.className = "card";

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="badge badge-info">Compensation Fairness Analysis</span>
                <span class="badge ${c.color === 'emerald' ? 'badge-success' : c.color === 'amber' ? 'badge-warning' : 'badge-primary'}">${c.equity_tag}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem; margin-bottom:1.25rem;">
                <div style="background:var(--bg-input); padding:0.85rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.75rem; color:var(--text-muted);">Your Current Salary</div>
                    <div style="font-size:1.6rem; font-weight:800; color:var(--text-primary);">${formatCurrency(c.actual_salary)}<span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">/mo</span></div>
                </div>
                <div style="background:var(--bg-input); padding:0.85rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.75rem; color:var(--text-muted);">ML Market Benchmark</div>
                    <div style="font-size:1.6rem; font-weight:800; color:var(--secondary);">${formatCurrency(c.benchmark_salary)}<span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">/mo</span></div>
                </div>
            </div>
            <div style="font-size:0.9rem; line-height:1.5; color:var(--text-secondary); background:var(--bg-input); padding:0.85rem; border-radius:var(--radius-md);">
                ${c.advice}
            </div>
        `;
        container.appendChild(card);
    }

    // 5. Skill Gap & Curriculum Card
    if (results.skill_gap) {
        const s = results.skill_gap;
        const card = document.createElement("div");
        card.className = "card";
        card.style.gridColumn = "1 / -1";

        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="badge badge-primary">Skill Gap & Upskilling Curriculum</span>
                <span class="badge ${s.hours_deficit === 0 ? 'badge-success' : 'badge-warning'}">${s.status}</span>
            </div>
            <p style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:1rem;">
                Completed <strong>${s.current_training_hours} hrs</strong> of training in the last year against the enterprise growth target of <strong>${s.recommended_target_hours} hrs</strong>.
            </p>
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:0.85rem; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted);">
                            <th style="padding:0.6rem;">Competency Focus</th>
                            <th style="padding:0.6rem;">Current Tier</th>
                            <th style="padding:0.6rem;">Target Tier</th>
                            <th style="padding:0.6rem;">Recommended Actionable Curriculum</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${s.curriculum.map(c => `
                            <tr style="border-bottom:1px solid var(--border-color);">
                                <td style="padding:0.75rem 0.6rem; font-weight:600;">${c.skill}</td>
                                <td style="padding:0.75rem 0.6rem;"><span class="badge badge-warning">${c.current_level}</span></td>
                                <td style="padding:0.75rem 0.6rem;"><span class="badge badge-success">${c.target_level}</span></td>
                                <td style="padding:0.75rem 0.6rem; color:var(--text-secondary);">${c.course}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        container.appendChild(card);
    }
}

