# Employee Performance & Prediction Pipeline

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

An end-to-end, full-stack Data Mining and Machine Learning web application designed to forecast employee promotional readiness, flight/attrition risk, performance percentiles, and compensation equity.

Built specifically for educational evaluation in Data Mining / Machine Learning project-based learning (PBL), this platform provides complete mathematical transparency into every stage of the pipeline: **Data Ingestion &rarr; Missing Value Imputation &rarr; IQR Outlier Winsorization &rarr; Categorical Encoding &rarr; StandardScaler Normalization &rarr; SMOTE Imbalance Balancing &rarr; Multi-Model Supervised Training &rarr; Confusion Matrix Evaluation &rarr; Bias-Variance Tradeoff Analysis &rarr; Explainable AI (XAI)**.

---

## 🌟 Key Features

- **Professional Multi-Page Web Application:**
  - **Landing Page (`/`):** Clean hero section with architecture overview and clear call-to-action buttons.
  - **Authentication Pages (`/signup`, `/signin`):** Salted password hashing (PBKDF2-HMAC-SHA256) and JWT token session management. Includes a 1-click **"Auto-Fill Sample Credentials"** button for quick evaluations.
  - **Main Dashboard (`/dashboard`):** Personalized employee portal to manage 19 workforce attributes, load test personas (Fast-Track, Burnout Risk, Underpaid Senior, Developing Junior), trigger individual or comprehensive intelligence audits, and export PDF/CSV reports.
  - **Pipeline Visualizer (`/pipeline`):** Interactive 8-step visualizer breaking down the exact mathematical operations applied to the employee's data, featuring live hyperparameter re-training and JSON configuration export.
  - **Admin / Dataset Explorer (`/admin`):** High-level cohort analytics across departments, salary curves, and registered user directory.
- **Genuine Machine Learning & Data Mining Core:**
  - Real calculations powered by `pandas`, `scikit-learn`, and `imbalanced-learn` (no mock data or hardcoded probabilities).
  - Multi-model evaluation comparing **Logistic Regression**, **Random Forest**, and **Gradient Boosting**.
  - Interactive **2x2 Confusion Matrix** with Type I and Type II error analysis tailored to talent management.
  - **Bias-Variance Diagnosis** with 5-Fold Stratified Cross-Validation and 5-point sample complexity learning curves.
  - **Explainable AI (XAI):** Local feature attributions highlighting positive catalysts, risk drivers, and prescriptive growth recommendations.
- **Modern UI / UX:**
  - Pure HTML5, CSS3, and modern Vanilla JavaScript (no heavy frontend frameworks required).
  - Smooth dark/light mode toggle with persistent state in `localStorage`.
  - Non-blocking toast notifications and animated loading skeletons.
  - Fully responsive on mobile, tablet, and desktop viewports.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3 (Custom Variables & Glassmorphism), Vanilla JavaScript (ES6+), Responsive Grid |
| **Backend** | Python 3.10+, FastAPI, Uvicorn (ASGI) |
| **Data Mining & ML** | Pandas, NumPy, Scikit-Learn, Imbalanced-Learn (SMOTE), SciPy |
| **Persistence** | SQLite3 (File-based, zero configuration), PBKDF2 Password Hashing, PyJWT |
| **Automation** | Windows Batch Script (`start.bat`) |

---

## 🚀 How to Run

### Method 1: One-Click Launch (Windows)
Double-click `start.bat` in the project root directory.

The batch script automatically:
1. Detects Python.
2. Creates a virtual environment in `.\venv` if it doesn't already exist.
3. Activates the virtual environment and installs dependencies from `requirements.txt`.
4. Starts the Uvicorn ASGI server at `http://127.0.0.1:8000`.
5. Opens your default web browser directly to `http://localhost:8000`.

### Method 2: Manual Terminal Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Data-Mining-PBL-Sem5-
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell / Command Prompt)
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the FastAPI application:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Open your browser:**
   Navigate to [http://localhost:8000](http://localhost:8000).

---

## 🔑 Pre-Configured Demo Credentials

For quick evaluation without manual registration, you can use the pre-seeded account:
- **Email:** `alex.rivera@enterprise.ai`
- **Password:** `Pipeline2026!`

*(You can also click the **"⚡ Click to Auto-Fill Sample Credentials"** button on the `/signin` page to populate these automatically).*

---

## 📁 Project Structure

```
Data-Mining-PBL-Sem5-/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Paths, secret keys, token lifetimes
│   ├── database.py               # SQLite initialization, schema, user seeding
│   ├── auth.py                   # PBKDF2 hashing, JWT encoding/decoding, guards
│   ├── main.py                   # FastAPI application, lifespan, static mounting
│   ├── models/                   # DB definitions
│   ├── schemas/
│   │   └── schemas.py            # Pydantic request/response validation schemas
│   ├── ml_pipeline/
│   │   ├── __init__.py
│   │   ├── data_generator.py     # 1,500 record synthetic HR dataset generator
│   │   ├── preprocessor.py       # Imputation, IQR winsorization, encoding, scaling
│   │   ├── feature_engineering.py# Domain ratios, Mutual Information, Gini ranking
│   │   ├── imbalance.py          # SMOTE resampling & before/after distributions
│   │   ├── trainer.py            # Logistic Regression, Random Forest, Gradient Boosting
│   │   ├── explainer.py          # Local feature impact attribution, XAI
│   │   └── pipeline_manager.py   # Master singleton orchestrating pipeline stages
│   └── routers/
│       ├── auth_router.py        # /api/auth (signup, signin, session, me)
│       ├── employee_router.py    # /api/employee (profile CRUD, test presets)
│       ├── analysis_router.py    # /api/analysis (model execution, history, CSV export)
│       ├── pipeline_router.py    # /api/pipeline (telemetry, live retrain, config export)
│       └── admin_router.py       # /api/admin (dataset stats, user registry)
├── data/
│   ├── synthetic_employee_data.csv # Generated dataset
│   └── employee_pipeline.db      # SQLite database
├── static/
│   ├── css/
│   │   └── styles.css            # Dark/light theme, glassmorphism, responsive grid
│   └── js/
│       ├── common.js             # Theme toggle, toasts, formatters, API client
│       ├── auth.js               # Sign up and Sign in controller
│       ├── dashboard.js          # Profile management and analysis triggers
│       ├── pipeline.js           # 8-step interactive pipeline visualizer
│       └── admin.js              # Cohort and user directory controller
├── templates/
│   ├── index.html                # Welcome landing page
│   ├── signup.html               # User registration page
│   ├── signin.html               # User sign-in page
│   ├── dashboard.html            # Main employee dashboard
│   ├── pipeline.html             # Pipeline visualizer page
│   └── admin.html                # Dataset explorer & admin directory
├── IMPLEMENTATION.md             # In-depth technical task documentation
├── README.md                     # Project documentation & execution guide
├── requirements.txt              # Production Python package requirements
└── start.bat                     # Windows 1-click startup automation script
```

---

## 🔬 Data Mining Techniques Implemented

1. **Missing Data Imputation:**
   - Median imputation ($\tilde{x}$) for continuous features to mitigate skewness.
   - Mode imputation for categorical features.
2. **IQR Outlier Winsorization:**
   - Detects extreme outliers beyond $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$ in continuous fields (e.g. salary, distance) and bounds them to safeguard gradient stability.
3. **Categorical Feature Encoding:**
   - Ordinal mapping for monotonic rankings (education, satisfaction).
   - One-Hot dummy encoding for nominal variables (department, job role, overtime).
4. **Z-Score Normalization (StandardScaler):**
   - Rescales all numeric dimensions to zero mean ($\mu = 0$) and unit variance ($\sigma = 1$).
5. **Domain Feature Engineering:**
   - Computes behavioral ratios: tenure-to-age ratio, role stability ratio, income per year of experience, burnout risk index, and growth momentum.
6. **Class Imbalance Handling (SMOTE):**
   - Synthesizes artificial minority vectors via $k$-nearest neighbors ($k=5$), elevating minority representation from ~17% to 50% without simple duplicate memorization.
7. **Supervised Classification & Regression:**
   - Benchmarks Logistic Regression (linear baseline), Random Forest (bagging ensemble), and Gradient Boosting (boosting ensemble).
   - Random Forest Regressor for market-fair compensation estimation.
8. **Evaluation Metrics:**
   - Accuracy, Precision, Recall, F1-Score, ROC-AUC, 2x2 Confusion Matrices, and ROC curves.
9. **Bias-Variance Tradeoff Analysis:**
   - Measures training vs test loss gap, 5-Fold Stratified Cross-Validation variance ($\pm \sigma$), and 5-point learning curve convergence.
10. **Explainable AI (XAI):**
    - Local feature attributions providing interpretable positive catalysts and drag factors for individual employees.

---

## 📸 Application Screenshots

| Page | Description |
|---|---|
| **Welcome Page (`/`)** | Hero banner with feature cards and direct access to Sign In and Registration. |
| **Dashboard (`/dashboard`)** | Employee profile editor, preset selector, and 5 predictive intelligence analysis cards. |
| **Pipeline Visualizer (`/pipeline`)** | 8-step interactive stepper with confusion matrix, SMOTE comparison, and live retraining. |
| **Dataset Explorer (`/admin`)** | Cohort distributions, department benchmarks, and registered user directory. |

---

## 🔮 Future Improvements

- [ ] **SHAP TreeExplainer:** Integrate exact Shapley value waterfalls for higher tree explainer fidelity.
- [ ] **Role Transition Simulator:** "What-if" scenario playground allowing employees to project future promotion odds based on prospective training goals.
- [ ] **Automated PDF Export:** Direct PDF rendering using WeasyPrint or headless browser integration.
- [ ] **Docker Containerization:** Dockerfile and Docker Compose configurations for one-command multi-platform deployment.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

