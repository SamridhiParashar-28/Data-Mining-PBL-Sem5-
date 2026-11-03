// Authentication Handlers (Signup & Signin)

document.addEventListener("DOMContentLoaded", () => {
    // Signup Form Handler
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = signupForm.querySelector("button[type='submit']");
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = "Creating Account...";

            const payload = {
                name: document.getElementById("name").value.trim(),
                email: document.getElementById("email").value.trim(),
                password: document.getElementById("password").value,
                employee_id: document.getElementById("employee_id") ? document.getElementById("employee_id").value.trim() : null,
                department: document.getElementById("department") ? document.getElementById("department").value : "Engineering"
            };

            try {
                const res = await apiFetch("/api/auth/signup", {
                    method: "POST",
                    body: JSON.stringify(payload)
                });
                if (res && res.success) {
                    showToast("Account created successfully! Redirecting to sign in...", "success");
                    setTimeout(() => {
                        window.location.href = "/signin?registered=true";
                    }, 1200);
                }
            } catch (err) {
                // Error shown by apiFetch toast
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Signin Form Handler
    const signinForm = document.getElementById("signin-form");
    if (signinForm) {
        // Check for registered param
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("registered") === "true") {
            showToast("Registration complete! Please enter your credentials.", "info");
        }

        signinForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = signinForm.querySelector("button[type='submit']");
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = "Signing in...";

            const payload = {
                email: document.getElementById("email").value.trim(),
                password: document.getElementById("password").value
            };

            try {
                const res = await apiFetch("/api/auth/signin", {
                    method: "POST",
                    body: JSON.stringify(payload)
                });
                if (res && res.access_token) {
                    setToken(res.access_token);
                    setUser(res.user);
                    showToast(`Welcome back, ${res.user.name}!`, "success");
                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 800);
                }
            } catch (err) {
                // Error handled by toast
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });

        // Quick Demo Fill Button
        const demoFillBtn = document.getElementById("demo-fill-btn");
        if (demoFillBtn) {
            demoFillBtn.addEventListener("click", () => {
                document.getElementById("email").value = "alex.rivera@enterprise.ai";
                document.getElementById("password").value = "Pipeline2026!";
                showToast("Demo credentials populated!", "info");
            });
        }
    }
});

