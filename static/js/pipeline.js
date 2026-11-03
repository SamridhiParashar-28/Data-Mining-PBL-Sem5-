// Pipeline Visualizer Controller

let pipelineData = null;
let currentStepIndex = 1;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch Pipeline Telemetry
    await fetchTelemetry();

    // 2. Setup Stepper Navigation
    setupStepper();

    // 3. Setup Retrain Panel
    setupRetrain();

    // 4. Setup Export JSON
    const exportBtn = document.getElementById("export-pipeline-btn");
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            window.location.href = "/api/pipeline/export-config";
        });
    }
});

async function fetchTelemetry() {
    try {
        const data = await apiFetch("/api/pipeline/visualize");
        if (data) {
            pipelineData = data;
            renderCurrentStep();
        }
    } catch (err) {
        console.error("Failed to load telemetry", err);
    }
}

function setupStepper() {
    const steps = document.querySelectorAll(".step-item");
    steps.forEach(step => {
        step.addEventListener("click", () => {
            const stepNum = parseInt(step.getAttribute("data-step"));
            goToStep(stepNum);
        });
    });

    const prevBtn = document.getElementById("prev-step-btn");
    const nextBtn = document.getElementById("next-step-btn");

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            if (currentStepIndex > 1) goToStep(currentStepIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            if (currentStepIndex < 8) goToStep(currentStepIndex + 1);
        });
    }
}

function goToStep(index) {
    currentStepIndex = index;

    // Update stepper classes
    document.querySelectorAll(".step-item").forEach(item => {
        const stepNum = parseInt(item.getAttribute("data-step"));
        item.classList.remove("active", "completed");
        if (stepNum === currentStepIndex) {
            item.classList.add("active");
        } else if (stepNum < currentStepIndex) {
            item.classList.add("completed");
        }
    });

    // Update Buttons
    const prevBtn = document.getElementById("prev-step-btn");
    const nextBtn = document.getElementById("next-step-btn");
    if (prevBtn) prevBtn.disabled = currentStepIndex === 1;
    if (nextBtn) nextBtn.textContent = currentStepIndex === 8 ? "Finish Review" : "Next Step →";

    renderCurrentStep();
    window.scrollTo({ top: 180, behavior: "smooth" });
}

function renderCurrentStep() {
    if (!pipelineData) return;
    const container = document.getElementById("pipeline-step-content");
    container.innerHTML = "";

    switch (currentStepIndex) {
        case 1:
            renderStepA(container);
            break;
        case 2:
            renderStepB(container);
            break;
        case 3:
            renderStepC(container);
            break;
        case 4:
            renderStepD(container);
            break;
        case 5:
            renderStepE(container);
            break;
        case 6:
            renderStepF(container);
            break;
        case 7:
            renderStepG(container);
            break;
        case 8:
            renderStepH(container);
            break;
    }
}

// --- Step 1: Raw Data Ingestion ---
function renderStepA(container) {
    const step = pipelineData.step_a_ingestion;
    const d = step.data;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>
            
            <div class="grid-4" style="margin-bottom:1.5rem;">
                <div style="background:var(--bg-input); padding:1rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.8rem; color:var(--text-muted);">Total Ingested Records</div>
                    <div style="font-size:2rem; font-weight:800; color:var(--primary);">${d.total_records}</div>
                </div>
                <div style="background:var(--bg-input); padding:1rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.8rem; color:var(--text-muted);">Raw Feature Columns</div>
                    <div style="font-size:2rem; font-weight:800; color:var(--secondary);">${d.total_columns}</div>
                </div>
                <div style="background:var(--bg-input); padding:1rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.8rem; color:var(--text-muted);">Promotion Target Ratio</div>
                    <div style="font-size:2rem; font-weight:800; color:var(--success);">${d.promotion_distribution.promotion_rate_pct}%</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${d.promotion_distribution.promoted} of ${d.total_records}</div>
                </div>
                <div style="background:var(--bg-input); padding:1rem; border-radius:var(--radius-md);">
                    <div style="font-size:0.8rem; color:var(--text-muted);">Attrition Target Ratio</div>
                    <div style="font-size:2rem; font-weight:800; color:var(--danger);">${d.attrition_distribution.attrition_rate_pct}%</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${d.attrition_distribution.attrited} of ${d.total_records}</div>
                </div>
            </div>

            <h3 style="margin-bottom:0.75rem; font-size:1.1rem;">Raw Ingestion Sample (First 5 Records)</h3>
            <div style="overflow-x:auto; background:var(--bg-input); border-radius:var(--radius-md); padding:0.5rem;">
                <table style="width:100%; border-collapse:collapse; font-size:0.8rem; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted);">
                            <th style="padding:0.5rem;">ID</th>
                            <th style="padding:0.5rem;">Age</th>
                            <th style="padding:0.5rem;">Department</th>
                            <th style="padding:0.5rem;">Role</th>
                            <th style="padding:0.5rem;">Monthly Income</th>
                            <th style="padding:0.5rem;">Tenure</th>
                            <th style="padding:0.5rem;">Rating</th>
                            <th style="padding:0.5rem;">Projects</th>
                            <th style="padding:0.5rem;">Overtime</th>
                            <th style="padding:0.5rem;">Promoted</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${d.sample_rows.map(r => `
                            <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                                <td style="padding:0.5rem; font-weight:600;">${r.employee_id}</td>
                                <td style="padding:0.5rem;">${r.age}</td>
                                <td style="padding:0.5rem;">${r.department}</td>
                                <td style="padding:0.5rem;">${r.job_role}</td>
                                <td style="padding:0.5rem;">${r.monthly_income ? formatCurrency(r.monthly_income) : '<span class="badge badge-warning">NaN</span>'}</td>
                                <td style="padding:0.5rem;">${r.years_at_company} yrs</td>
                                <td style="padding:0.5rem;">${r.performance_rating}/5</td>
                                <td style="padding:0.5rem;">${r.projects_completed}</td>
                                <td style="padding:0.5rem;">${r.overtime}</td>
                                <td style="padding:0.5rem;"><span class="badge ${r.promoted === 1 ? 'badge-success' : 'badge-primary'}">${r.promoted}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div style="margin-top:1.25rem; font-size:0.85rem; color:var(--text-secondary); background:rgba(99, 102, 241, 0.08); padding:0.85rem; border-radius:var(--radius-md); border-left:4px solid var(--primary);">
                💡 <strong>Data Mining Concept:</strong> Raw transactional databases contain skewed continuous values, missing fields, and severe class imbalances. Notice how only ~17% of employees are promoted; a naive model guessing '0' would have 83% accuracy while offering zero practical business value!
            </div>
        </div>
    `;
}

// --- Step 2: Preprocessing ---
function renderStepB(container) {
    const step = pipelineData.step_b_preprocessing;
    const d = step.data;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div class="grid-2" style="margin-bottom:1.5rem;">
                <!-- Missing Value Imputation -->
                <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md);">
                    <h3 style="font-size:1rem; margin-bottom:0.75rem; color:var(--primary);">1. Missing Value Imputation</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:1rem;">
                        Median imputation preserves distribution centers against extreme values, while Mode handles discrete categoricals.
                    </p>
                    <table style="width:100%; border-collapse:collapse; font-size:0.8rem;">
                        <thead>
                            <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted); text-align:left;">
                                <th style="padding:0.4rem;">Feature</th>
                                <th style="padding:0.4rem;">Missing Found</th>
                                <th style="padding:0.4rem;">Strategy</th>
                                <th style="padding:0.4rem;">Imputed Val</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(d.missing_values).map(([k, v]) => `
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                                    <td style="padding:0.4rem; font-weight:600;">${k}</td>
                                    <td style="padding:0.4rem;"><span class="badge badge-warning">${v.missing_count} rows</span></td>
                                    <td style="padding:0.4rem;">${v.imputed_with}</td>
                                    <td style="padding:0.4rem; font-weight:600;">${v.value}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Outlier Handling -->
                <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md);">
                    <h3 style="font-size:1rem; margin-bottom:0.75rem; color:var(--secondary);">2. Outlier Detection & IQR Winsorization</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:1rem;">
                        Values beyond [Q1 - 1.5×IQR, Q3 + 1.5×IQR] are capped to protect linear and distance estimators from gradient explosion.
                    </p>
                    <table style="width:100%; border-collapse:collapse; font-size:0.8rem;">
                        <thead>
                            <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted); text-align:left;">
                                <th style="padding:0.4rem;">Feature</th>
                                <th style="padding:0.4rem;">IQR Bounds</th>
                                <th style="padding:0.4rem;">Outliers Clipped</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(d.outliers_detected).map(([k, v]) => `
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                                    <td style="padding:0.4rem; font-weight:600;">${k}</td>
                                    <td style="padding:0.4rem;">[${v.lower_bound}, ${v.upper_bound}]</td>
                                    <td style="padding:0.4rem;"><span class="badge badge-success">${v.outliers_clipped} records</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Encoding & Scaling -->
            <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md); margin-bottom:1.5rem;">
                <h3 style="font-size:1rem; margin-bottom:0.75rem; color:var(--accent);">3. One-Hot Encoding & StandardScaler (Z-Score Normalization)</h3>
                <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.75rem;">
                    Categorical nominal attributes (department, role, education field, overtime) were expanded via One-Hot Encoding. All <strong>${d.encoded_features_count}</strong> features were normalized to μ = 0, σ = 1 via formula: <em>z = (x - μ) / σ</em>.
                </p>
                <div style="display:flex; flex-wrap:wrap; gap:0.4rem; max-height:120px; overflow-y:auto; padding:0.5rem; background:var(--bg-primary); border-radius:var(--radius-sm);">
                    ${d.feature_names.map(f => `<span class="badge badge-primary" style="font-size:0.7rem;">${f}</span>`).join('')}
                </div>
            </div>
        </div>
    `;
}

// --- Step 3: Feature Engineering ---
function renderStepC(container) {
    const step = pipelineData.step_c_feature_engineering;
    const pFeatures = step.promotion_features.top_features;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div class="grid-2" style="margin-bottom:1.5rem;">
                <div>
                    <h3 style="font-size:1rem; margin-bottom:0.75rem; color:var(--primary);">Engineered Domain Ratios</h3>
                    <ul style="font-size:0.85rem; color:var(--text-secondary); line-height:1.8; margin-left:1.2rem;">
                        <li><strong>Tenure-to-Age Ratio:</strong> <code>years_at_company / (age - 18)</code> - captures internal organizational loyalty.</li>
                        <li><strong>Role Stability Ratio:</strong> <code>years_in_current_role / (years_at_company + 1)</code> - detects stagnation vs agility.</li>
                        <li><strong>Income per Year Experience:</strong> <code>salary / (total_working_years + 1)</code> - compensation velocity.</li>
                        <li><strong>Burnout Index:</strong> <code>(overtime_flag * 1.5) + (5 - work_life_balance) + (projects / 10)</code>.</li>
                        <li><strong>Growth Momentum:</strong> <code>(training_hours / 35.0) * (performance_rating / 3.5)</code>.</li>
                    </ul>
                </div>
                <div>
                    <h3 style="font-size:1rem; margin-bottom:0.75rem; color:var(--secondary);">Feature Importance Ranking (Gini Impurity & Information Gain)</h3>
                    <div style="display:flex; flex-direction:column; gap:0.5rem;">
                        ${pFeatures.slice(0, 6).map(f => `
                            <div>
                                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:0.2rem;">
                                    <span>${f.clean_name}</span>
                                    <span>${f.relative_weight_pct}% weight (MI: ${f.mutual_info})</span>
                                </div>
                                <div style="height:6px; background:var(--bg-input); border-radius:3px; overflow:hidden;">
                                    <div style="width:${f.relative_weight_pct * 3}%; height:100%; background:linear-gradient(90deg, var(--primary), var(--secondary));"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// --- Step 4: Class Imbalance Handling (SMOTE) ---
function renderStepD(container) {
    const step = pipelineData.step_d_imbalance;
    const smote = step.promotion_smote;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div class="grid-2" style="margin-bottom:1.5rem;">
                <!-- Before SMOTE -->
                <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md); border-top:4px solid var(--danger);">
                    <h3 style="font-size:1rem; margin-bottom:0.5rem;">Raw Training Distribution (Imbalanced)</h3>
                    <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem;">Imbalance Ratio: ${smote.before.imbalance_ratio}</p>
                    
                    <div style="display:flex; gap:1rem; margin-bottom:1rem;">
                        <div style="flex:1; background:var(--bg-card); padding:0.75rem; border-radius:var(--radius-sm); text-align:center;">
                            <div style="font-size:0.75rem; color:var(--text-muted);">Class 0 (Not Promoted)</div>
                            <div style="font-size:1.6rem; font-weight:800; color:var(--info);">${smote.before.class_0_count}</div>
                            <span class="badge badge-primary">${smote.before.class_0_pct}%</span>
                        </div>
                        <div style="flex:1; background:var(--bg-card); padding:0.75rem; border-radius:var(--radius-sm); text-align:center;">
                            <div style="font-size:0.75rem; color:var(--text-muted);">Class 1 (Promoted)</div>
                            <div style="font-size:1.6rem; font-weight:800; color:var(--warning);">${smote.before.class_1_count}</div>
                            <span class="badge badge-warning">${smote.before.class_1_pct}%</span>
                        </div>
                    </div>
                </div>

                <!-- After SMOTE -->
                <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md); border-top:4px solid var(--success);">
                    <h3 style="font-size:1rem; margin-bottom:0.5rem;">After SMOTE Resampling (Balanced)</h3>
                    <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:1rem;">Synthesized ${smote.synthetic_samples_generated} artificial minority vectors using k=5 nearest neighbors</p>

                    <div style="display:flex; gap:1rem; margin-bottom:1rem;">
                        <div style="flex:1; background:var(--bg-card); padding:0.75rem; border-radius:var(--radius-sm); text-align:center;">
                            <div style="font-size:0.75rem; color:var(--text-muted);">Class 0 (Not Promoted)</div>
                            <div style="font-size:1.6rem; font-weight:800; color:var(--info);">${smote.after.class_0_count}</div>
                            <span class="badge badge-primary">${smote.after.class_0_pct}%</span>
                        </div>
                        <div style="flex:1; background:var(--bg-card); padding:0.75rem; border-radius:var(--radius-sm); text-align:center;">
                            <div style="font-size:0.75rem; color:var(--text-muted);">Class 1 (Promoted)</div>
                            <div style="font-size:1.6rem; font-weight:800; color:var(--success);">${smote.after.class_1_count}</div>
                            <span class="badge badge-success">${smote.after.class_1_pct}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div style="font-size:0.85rem; color:var(--text-secondary); background:rgba(16, 185, 129, 0.08); padding:0.85rem; border-radius:var(--radius-md); border-left:4px solid var(--success);">
                💡 <strong>Why SMOTE Matters:</strong> ${smote.educational_note}
            </div>
        </div>
    `;
}

// --- Step 5: Multi-Model Training ---
function renderStepE(container) {
    const step = pipelineData.step_e_training;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div class="grid-3" style="margin-bottom:1.5rem;">
                ${step.models_compared.map(m => `
                    <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md); border-top:3px solid var(--primary);">
                        <span class="badge badge-primary" style="margin-bottom:0.5rem;">${m.type}</span>
                        <h3 style="font-size:1.1rem; margin-bottom:0.5rem;">${m.name}</h3>
                        <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.75rem;">
                            <strong>Strengths:</strong> ${m.advantages}
                        </div>
                        <div style="font-size:0.8rem; color:var(--text-muted); background:var(--bg-card); padding:0.5rem; border-radius:var(--radius-sm);">
                            <strong>HR Context:</strong> ${m.use_case}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// --- Step 6: Evaluation Metrics & Confusion Matrices ---
function renderStepF(container) {
    const step = pipelineData.step_f_evaluation;
    const metrics = step.promotion_metrics;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <!-- Models Performance Comparison Table -->
            <h3 style="font-size:1rem; margin-bottom:0.75rem;">Model Benchmark Comparison (Unseen Test Set)</h3>
            <div style="overflow-x:auto; margin-bottom:1.5rem;">
                <table style="width:100%; border-collapse:collapse; font-size:0.85rem; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted);">
                            <th style="padding:0.6rem;">Algorithm</th>
                            <th style="padding:0.6rem;">Accuracy</th>
                            <th style="padding:0.6rem;">Precision</th>
                            <th style="padding:0.6rem;">Recall</th>
                            <th style="padding:0.6rem;">F1-Score</th>
                            <th style="padding:0.6rem;">ROC-AUC</th>
                            <th style="padding:0.6rem;">5-Fold CV F1</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(metrics).map(([k, m]) => `
                            <tr style="border-bottom:1px solid var(--border-color);">
                                <td style="padding:0.75rem 0.6rem; font-weight:700;">${m.display_name}</td>
                                <td style="padding:0.75rem 0.6rem;"><span class="badge badge-primary">${(m.accuracy * 100).toFixed(1)}%</span></td>
                                <td style="padding:0.75rem 0.6rem;">${(m.precision * 100).toFixed(1)}%</td>
                                <td style="padding:0.75rem 0.6rem;">${(m.recall * 100).toFixed(1)}%</td>
                                <td style="padding:0.75rem 0.6rem; font-weight:700; color:var(--success);">${(m.f1_score * 100).toFixed(1)}%</td>
                                <td style="padding:0.75rem 0.6rem; font-weight:700; color:var(--secondary);">${(m.roc_auc * 100).toFixed(1)}%</td>
                                <td style="padding:0.75rem 0.6rem;">${(m.cv_f1_mean * 100).toFixed(1)}% ± ${(m.cv_f1_std * 100).toFixed(1)}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Confusion Matrix Display for Best Model -->
            <h3 style="font-size:1rem; margin-bottom:0.5rem;">Interactive Confusion Matrix (Promotion Classification)</h3>
            <div class="grid-2">
                <div>
                    <div class="confusion-matrix-grid">
                        <div></div>
                        <div class="cm-header">Pred: No (0)</div>
                        <div class="cm-header">Pred: Yes (1)</div>

                        <div class="cm-header">Actual: No</div>
                        <div class="cm-cell cm-correct">
                            <div class="cm-value" style="color:var(--success);">${metrics.gradient_boosting.confusion_matrix.tn}</div>
                            <div class="cm-label">True Negative (TN)</div>
                        </div>
                        <div class="cm-cell cm-incorrect">
                            <div class="cm-value" style="color:var(--danger);">${metrics.gradient_boosting.confusion_matrix.fp}</div>
                            <div class="cm-label">False Positive (Type I)</div>
                        </div>

                        <div class="cm-header">Actual: Yes</div>
                        <div class="cm-cell cm-incorrect">
                            <div class="cm-value" style="color:var(--danger);">${metrics.gradient_boosting.confusion_matrix.fn}</div>
                            <div class="cm-label">False Negative (Type II)</div>
                        </div>
                        <div class="cm-cell cm-correct">
                            <div class="cm-value" style="color:var(--success);">${metrics.gradient_boosting.confusion_matrix.tp}</div>
                            <div class="cm-label">True Positive (TP)</div>
                        </div>
                    </div>
                </div>
                <div style="background:var(--bg-input); padding:1rem; border-radius:var(--radius-md); font-size:0.85rem;">
                    <h4 style="margin-bottom:0.5rem; color:var(--primary);">Data Mining Error Analysis:</h4>
                    <p style="color:var(--text-secondary); margin-bottom:0.75rem;">
                        <strong>Type I Error (False Positive):</strong> Model predicted promotion, but candidate wasn't ready. Risk: Disillusionment if promoted prematurely.
                    </p>
                    <p style="color:var(--text-secondary); margin-bottom:0.75rem;">
                        <strong>Type II Error (False Negative):</strong> Model missed a high performer. Risk: Frustrated employee leaves for competitor! In HR, minimizing False Negatives (maximizing Recall) is critical.
                    </p>
                </div>
            </div>
        </div>
    `;
}

// --- Step 7: Bias-Variance Analysis ---
function renderStepG(container) {
    const step = pipelineData.step_g_bias_variance;
    const bv = step.promotion_bias_variance;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-primary">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div class="grid-3" style="margin-bottom:1.5rem;">
                ${Object.entries(bv.models).map(([k, m]) => `
                    <div style="background:var(--bg-input); padding:1.25rem; border-radius:var(--radius-md);">
                        <h3 style="font-size:1.05rem; margin-bottom:0.5rem;">${m.display_name}</h3>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.3rem;">
                            <span style="color:var(--text-muted);">Train Accuracy:</span>
                            <span style="font-weight:700;">${(m.train_accuracy * 100).toFixed(1)}%</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.3rem;">
                            <span style="color:var(--text-muted);">Test Accuracy:</span>
                            <span style="font-weight:700;">${(m.test_accuracy * 100).toFixed(1)}%</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.75rem;">
                            <span style="color:var(--text-muted);">Generalization Gap:</span>
                            <span style="font-weight:700; color:${m.acc_gap > 0.08 ? 'var(--warning)' : 'var(--success)'};">${(m.acc_gap * 100).toFixed(1)}%</span>
                        </div>
                        <div style="font-size:0.78rem; background:var(--bg-card); padding:0.5rem; border-radius:var(--radius-sm); color:var(--text-secondary);">
                            ${m.diagnosis}
                        </div>
                    </div>
                `).join('')}
            </div>

            <!-- Learning Curve Table -->
            <h3 style="font-size:1rem; margin-bottom:0.5rem;">Empirical Learning Curve (Convergence Dynamics)</h3>
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:0.85rem; text-align:left;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border-color); color:var(--text-muted);">
                            <th style="padding:0.5rem;">Training Subsample Size</th>
                            <th style="padding:0.5rem;">Training Score</th>
                            <th style="padding:0.5rem;">Validation Score (Cross-Validation)</th>
                            <th style="padding:0.5rem;">Empirical Bias-Variance Assessment</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${bv.learning_curve.map(pt => `
                            <tr style="border-bottom:1px solid var(--border-color);">
                                <td style="padding:0.6rem; font-weight:600;">${pt.sample_size} samples</td>
                                <td style="padding:0.6rem;">${(pt.train_score * 100).toFixed(1)}%</td>
                                <td style="padding:0.6rem; font-weight:700; color:var(--secondary);">${(pt.val_score * 100).toFixed(1)}%</td>
                                <td style="padding:0.6rem; color:var(--text-secondary); font-size:0.8rem;">
                                    ${pt.train_score - pt.val_score < 0.1 ? 'Curves converging. High sample efficiency.' : 'Variance gap narrowing with additional data.'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// --- Step 8: Final Prediction & Explanation ---
function renderStepH(container) {
    const step = pipelineData.step_h_inference;

    container.innerHTML = `
        <div class="card" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h2>${step.title}</h2>
                <span class="badge badge-success">${step.badge}</span>
            </div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">${step.summary}</p>

            <div style="background:var(--bg-input); padding:1.5rem; border-radius:var(--radius-md); margin-bottom:1.5rem;">
                <h3 style="font-size:1.1rem; margin-bottom:0.75rem; color:var(--primary);">End-to-End Inference Traceability</h3>
                <p style="font-size:0.88rem; color:var(--text-secondary); line-height:1.6; margin-bottom:1rem;">
                    When an employee updates their profile on the Dashboard, their raw inputs traverse the identical mathematical steps verified in this pipeline:
                </p>
                <ol style="margin-left:1.5rem; font-size:0.85rem; color:var(--text-secondary); line-height:1.8;">
                    <li><strong>Missing Imputation:</strong> Any blank attributes default to median/mode.</li>
                    <li><strong>Outlier Winsorization:</strong> Values are bounded by Q1-1.5*IQR to Q3+1.5*IQR.</li>
                    <li><strong>One-Hot Encoding:</strong> Categoricals map into 28 standardized binary dimensions.</li>
                    <li><strong>StandardScaler:</strong> Inputs standardized: <em>z = (x - μ) / σ</em>.</li>
                    <li><strong>Ensemble Inference:</strong> Best estimators (Gradient Boosting & Random Forest) compute log-odds and calibrated probabilities.</li>
                    <li><strong>Explainable AI:</strong> Local feature attributions decompose the prediction into positive catalysts, risk drivers, and actionable upskilling steps.</li>
                </ol>
            </div>

            <div style="text-align:center;">
                <a href="/dashboard" class="btn btn-primary">Return to Personal Dashboard & Run Analysis →</a>
            </div>
        </div>
    `;
}

// --- Retrain Live Panel ---
function setupRetrain() {
    const retrainForm = document.getElementById("retrain-form");
    if (!retrainForm) return;

    retrainForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("retrain-submit-btn");
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = "<span>Retraining Pipeline...</span>";

        const testSize = parseFloat(document.getElementById("retrain-test-size").value);
        const nEstimators = parseInt(document.getElementById("retrain-n-estimators").value);
        const applySmote = document.getElementById("retrain-apply-smote").checked;

        try {
            const res = await apiFetch("/api/pipeline/retrain", {
                method: "POST",
                body: JSON.stringify({
                    test_size: testSize,
                    n_estimators: nEstimators,
                    apply_smote: applySmote,
                    random_state: 42
                })
            });

            if (res && res.success) {
                pipelineData = res.telemetry;
                renderCurrentStep();
                showToast("Pipeline retrained with new hyperparameters!", "success");
            }
        } catch (err) {
            // Handled
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    });
}

