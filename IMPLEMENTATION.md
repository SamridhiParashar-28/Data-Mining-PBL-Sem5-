# Implementation Documentation: Employee Performance & Prediction Pipeline

## 1. Project Overview & Scope
The **Employee Performance & Prediction Pipeline** is a multi-page web application and comprehensive Data Mining / Machine Learning engineering system. It provides employees and human capital managers with predictive insights regarding:
- **Promotion Probability** (binary classification with calibrated probability)
- **Job Change / Attrition Risk** (binary classification with flight risk tiering)
- **Performance Band & Peer Percentile Ranking** (multi-dimensional composite scoring)
- **Skill Gap & Upskilling Curriculum** (prescriptive training path generation)
- **Compensation Fairness Analysis** (continuous ML regression benchmarking)

Unlike opaque "black-box" prototypes, this system is built around an **educational, fully inspectable Data Mining pipeline** that exposes all 8 stages from raw data ingestion to explainable model inferences.

---

## 2. System Architecture & Component Mapping

```
                               ┌──────────────────────────────────────────────┐
                               │           Client Layer (Browser)             │
                               │  HTML5 + CSS3 + Vanilla JavaScript (ES6+)    │
                               │  (Dark / Light Mode, Responsive UI, Toasts)  │
                               └──────────────────────┬───────────────────────┘
                                                      │ HTTP / REST / JSON
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │             FastAPI Backend (Python)         │
                               │  Routers, JWT Auth, Session Cookie Management│
                               └───────────┬──────────────────────┬───────────┘
                                           │                      │
                   ┌───────────────────────▼───────┐      ┌───────▼──────────────────────┐
                   │    SQLite Persistence Layer   │      │   Data Mining Pipeline Engine│
                   │  - users                      │      │  (Pandas, Scikit-Learn,      │
                   │  - employee_profiles          │      │   Imbalanced-Learn)          │
                   │  - analysis_history           │      └──────────────────────────────┘
                   └───────────────────────────────┘
```

---

## 3. Data Mining Pipeline Stages & Detailed Task Documentation

### Task 1: Realistic Data Ingestion & Profiling
- **Module:** `app/ml_pipeline/data_generator.py`
- **Data Attributes:** Generates 1,500 enterprise records encompassing demographics, tenure, organizational variables, and performance ratings.
- **Controlled Class Imbalance:** Positive outcomes in talent analytics (promotions and departures) are inherently rare. The generator calibrates the log-odds distributions such that promotion is ~17% and attrition is ~17%, creating a classic imbalanced learning problem.
- **Intentional Anomalies for Preprocessing Demonstration:**
  - 2.5% missing values injected into `training_hours_last_year` and `monthly_income`.
  - Outliers injected into `monthly_income` ($48,500) and `distance_from_home` (125 km) to showcase outlier detection algorithms.

### Task 2: Data Preprocessing & Cleaning
- **Module:** `app/ml_pipeline/preprocessor.py`
- **Missing Value Imputation:**
  - *Numerical Variables:* Imputed using the **Median** ($\tilde{x}$) to resist skewness from extreme values.
  - *Categorical Variables:* Imputed using the **Mode** (most frequent class).
- **Outlier Detection & Winsorization (IQR Method):**
  - Computes the first quartile ($Q_1$) and third quartile ($Q_3$).
  - Calculates the Interquartile Range: $IQR = Q_3 - Q_1$.
  - Bounds continuous features within $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$.
  - Values beyond these bounds are clipped/winsorized rather than discarded, preserving sample size while eliminating gradient instability.
- **Categorical Feature Encoding:**
  - *Ordinal Encoding:* Monotonic attributes (`education_level`, `performance_rating`, `job_satisfaction`, `work_life_balance`) preserve natural order.
  - *One-Hot Encoding:* Nominal variables (`department`, `job_role`, `education_field`, `overtime`) are expanded into orthogonal binary dummy variables (tracking 28 total encoded dimensions).
- **Feature Scaling (StandardScaler):**
  - Standardizes all features to zero mean ($\mu = 0$) and unit variance ($\sigma = 1$) using:
    $$z = \frac{x - \mu}{\sigma}$$
  - Crucial for distance-based estimators and gradient descent convergence.

### Task 3: Feature Engineering & Information-Theoretic Selection
- **Module:** `app/ml_pipeline/feature_engineering.py`
- **Domain Ratios Derived:**
  1. *Tenure-to-Age Ratio:* $\frac{\text{years\_at\_company}}{\max(\text{age} - 18, 1)}$ (measures organizational loyalty).
  2. *Role Stability Ratio:* $\frac{\text{years\_in\_current\_role}}{\text{years\_at\_company} + 1}$ (measures agility vs stagnation).
  3. *Income-per-Year Experience:* $\frac{\text{monthly\_income}}{\text{total\_working\_years} + 1}$ (compensation progression velocity).
  4. *Burnout Index:* $(1.5 \times \text{overtime\_flag}) + (5 - \text{work\_life\_balance}) + \frac{\text{projects}}{10}$.
  5. *Growth Momentum:* $(\frac{\text{training\_hours}}{35.0}) \times (\frac{\text{performance\_rating}}{3.5})$.
- **Feature Selection & Importance Ranking:**
  - Evaluates feature significance using **Random Forest Gini Impurity reduction** (Mean Decrease in Impurity) alongside **Mutual Information Gain** from Information Theory:
    $$I(X; Y) = \sum_{x \in X} \sum_{y \in Y} p(x, y) \log \frac{p(x, y)}{p(x)p(y)}$$

### Task 4: Class Imbalance Handling with SMOTE
- **Module:** `app/ml_pipeline/imbalance.py`
- **The Imbalance Challenge:** In an imbalanced dataset where 83% of employees are not promoted, a trivial classifier that always predicts 0 achieves an ostensibly high 83% accuracy, but has 0% recall on the minority class.
- **SMOTE (Synthetic Minority Over-sampling Technique):**
  - For each minority instance $\mathbf{x}_i$, SMOTE identifies its $k$ nearest neighbors in normalized feature space ($k=5$).
  - A neighbor $\mathbf{x}_{zi}$ is randomly selected, and a synthetic point is generated along the line segment:
    $$\mathbf{x}_{\text{new}} = \mathbf{x}_i + \lambda (\mathbf{x}_{zi} - \mathbf{x}_i), \quad \lambda \sim U(0, 1)$$
  - Equalizes the class distribution from 1,000 : 200 (83% / 17%) to 1,000 : 1,000 (50% / 50%) without naive duplicate cloning.

### Task 5: Multi-Model Supervised Training
- **Module:** `app/ml_pipeline/trainer.py`
- **Three Diverse Architectures Trained:**
  1. **Logistic Regression (L2 Regularized):**
     - Parametric linear classifier serving as the baseline.
     - Fast inference, stable log-odds coefficients, highly interpretable.
  2. **Random Forest Classifier (Bagging Ensemble):**
     - Bootstrap Aggregating with 100 decision trees and random feature subspaces.
     - Reduces estimator variance and handles non-linear decision thresholds.
  3. **Gradient Boosting Classifier (Boosting Ensemble):**
     - Sequential boosting fitting tree stumps to the pseudo-residuals of the loss function.
     - Minimizes bias and captures complex multivariate feature interactions.
- **Continuous Compensation Model:**
  - Fits a `RandomForestRegressor` mapping experience, education, performance, and role scope to fair market salary.

### Task 6: Rigorous Test-Set Evaluation & Confusion Matrices
- **Module:** `app/ml_pipeline/trainer.py`
- **Metrics Computed on Stratified Holdout Test Split:**
  - Accuracy: $\frac{TP + TN}{TP + TN + FP + FN}$
  - Precision: $\frac{TP}{TP + FP}$ (purity of positive predictions)
  - Recall: $\frac{TP}{TP + FN}$ (coverage of true positives)
  - F1-Score: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
  - ROC-AUC: Area under the Receiver Operating Characteristic curve.
- **Confusion Matrix Semantics in Talent Management:**
  - *Type I Error (False Positive):* Over-estimating readiness; promoting an unready candidate.
  - *Type II Error (False Negative):* Under-estimating readiness; missing an exemplary employee, driving them to depart for a competitor.

### Task 7: Bias-Variance Tradeoff Analysis
- **Module:** `app/ml_pipeline/trainer.py`
- **Generalization Gap Diagnosis:**
  - Contrasts Training Accuracy with Test Accuracy.
  - Large gaps (> 8%) indicate high variance (overfitting).
  - Low training accuracy (< 75%) indicates high bias (underfitting).
- **Stratified 5-Fold Cross-Validation:**
  - Measures the stability and standard deviation ($\pm \sigma$) of F1 scores across 5 independent partitions.
- **Learning Curve Convergence:**
  - Computes empirical training and cross-validation scores at 35%, 50%, 70%, 85%, and 100% of data volume, visualizing how sample complexity reduces variance.

### Task 8: Final Inference & Explainable AI (XAI)
- **Module:** `app/ml_pipeline/explainer.py`
- **Local Feature Attribution:**
  - Decomposes the individual employee's vector into top positive catalysts (e.g., high performance rating, velocity) and drag factors (e.g., lack of training hours, excessive overtime).
- **Prescriptive Guidance:**
  - Formulates actionable training milestones and workload adjustments.

---

## 4. API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/signup` | Register a new employee account | No |
| `POST` | `/api/auth/signin` | Sign in with email and password (returns JWT) | No |
| `GET` | `/api/auth/me` | Retrieve active authenticated session and profile | Yes (Bearer/Cookie) |
| `POST` | `/api/auth/signout` | Invalidate cookie and terminate session | No |
| `GET` | `/api/employee/profile` | Retrieve employee's profile attributes | Yes |
| `POST` | `/api/employee/profile` | Update employee's profile attributes | Yes |
| `GET` | `/api/employee/presets` | Get preset test profiles (Fast Track, Burnout, etc.) | No |
| `POST` | `/api/analysis/run` | Execute ML models for specified analysis | Yes |
| `GET` | `/api/analysis/history` | Retrieve historical analysis logs for current user | Yes |
| `GET` | `/api/analysis/export-csv` | Download complete individual assessment as CSV | Yes |
| `GET` | `/api/pipeline/visualize` | Retrieve full 8-stage pipeline telemetry | No |
| `POST` | `/api/pipeline/retrain` | Live retrain with custom hyperparameters | No |
| `GET` | `/api/pipeline/export-config`| Export pipeline architecture & metrics as JSON | No |
| `GET` | `/api/admin/stats` | Dataset statistics and registered user directory | No |

---

## 5. Database Schema (SQLite)

- **`users` Table:**
  - `id`: Integer Primary Key
  - `employee_id`: Unique identifier (e.g. `EMP-1001`)
  - `name`: Full Name
  - `email`: Unique email (case-insensitive)
  - `password_hash`: PBKDF2-HMAC-SHA256 with 16-byte random salt
  - `role`: Role string (`employee` or `admin`)
  - `department`: Organizational department
  - `created_at`: ISO-8601 UTC timestamp

- **`employee_profiles` Table:**
  - Stores all 19 raw and psychometric features with foreign key relation to `users.id`.

- **`analysis_history` Table:**
  - Records timestamped executions of analyses, summaries, and full result JSON payloads.

---

## 6. Execution & Verification Summary
- **Zero External Compilers Needed:** Pure Python cryptography (PBKDF2) and standard wheels avoid C++ build errors on Windows.
- **One-Click Startup:** `start.bat` provisions the virtual environment, installs `requirements.txt`, launches Uvicorn on `http://127.0.0.1:8000`, and opens the default web browser.
- **Pre-Seeded Demo Account:**
  - **Email:** `alex.rivera@enterprise.ai`
  - **Password:** `Pipeline2026!`
  - Can be populated with one click on the Sign In page.

