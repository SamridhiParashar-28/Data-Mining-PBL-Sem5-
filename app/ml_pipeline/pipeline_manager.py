import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.model_selection import train_test_split
from app.config import DATASET_PATH, ARTIFACTS_PATH
from app.ml_pipeline.data_generator import generate_synthetic_dataset
from app.ml_pipeline.preprocessor import DataMiningPreprocessor
from app.ml_pipeline.feature_engineering import FeatureEngineer
from app.ml_pipeline.imbalance import ImbalanceHandler
from app.ml_pipeline.trainer import PipelineTrainer
from app.ml_pipeline.explainer import PredictionExplainer

class PipelineManager:
    """
    Singleton orchestrator for the entire Data Mining & Machine Learning Pipeline.
    Manages raw ingestion, preprocessing, SMOTE re-sampling, model training,
    evaluation, bias-variance diagnostics, and real-time employee inferences.
    """

    def __init__(self):
        self.preprocessor = DataMiningPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.imbalance_handler = ImbalanceHandler()
        self.promo_trainer = PipelineTrainer(random_state=42)
        self.attrition_trainer = PipelineTrainer(random_state=42)
        
        self.raw_df = None
        self.pipeline_visualization_data = {}
        self.is_initialized = False

    def initialize(self, force_regenerate: bool = False):
        """Loads dataset (generating if missing), executes full pipeline, and prepares visualization metrics."""
        print("[PipelineManager] Initializing Data Mining Pipeline...")
        
        if not DATASET_PATH.exists() or force_regenerate:
            print("[PipelineManager] Generating synthetic dataset...")
            self.raw_df = generate_synthetic_dataset(num_samples=1500, save=True)
        else:
            self.raw_df = pd.read_csv(DATASET_PATH)

        self._fit_pipeline()
        self.is_initialized = True
        print("[PipelineManager] Pipeline initialization complete!")

    def _fit_pipeline(self, test_size: float = 0.20, n_estimators: int = 100, apply_smote: bool = True, random_state: int = 42):
        """Executes all 8 stages of the data mining pipeline with educational telemetry."""
        df = self.raw_df.copy()

        # Step A: Raw Data Ingestion Telemetry
        ingestion_data = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "missing_counts": {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0},
            "promotion_distribution": {
                "not_promoted": int((df["promoted"] == 0).sum()),
                "promoted": int((df["promoted"] == 1).sum()),
                "promotion_rate_pct": round(float(df["promoted"].mean() * 100), 2)
            },
            "attrition_distribution": {
                "retained": int((df["attrition"] == 0).sum()),
                "attrited": int((df["attrition"] == 1).sum()),
                "attrition_rate_pct": round(float(df["attrition"].mean() * 100), 2)
            },
            "sample_rows": df.head(5).to_dict(orient="records")
        }

        # Step B: Preprocessing (Imputation, Winsorization, One-Hot Encoding, Scaling)
        self.preprocessor = DataMiningPreprocessor()
        X_scaled, preproc_report = self.preprocessor.fit_transform(df)
        feature_names = self.preprocessor.feature_columns

        # Step C: Feature Engineering & Selection
        df_engineered = self.feature_engineer.derive_features(df)
        feature_importance_promo = self.feature_engineer.compute_feature_importances(
            X_scaled, df["promoted"].values, feature_names, target_name="Promotion"
        )
        feature_importance_attrition = self.feature_engineer.compute_feature_importances(
            X_scaled, df["attrition"].values, feature_names, target_name="Attrition"
        )

        # Step D: Class Imbalance Handling (SMOTE)
        y_promo = df["promoted"].values
        y_attr = df["attrition"].values

        # Split Train / Test (Stratified)
        X_train, X_test, y_promo_train, y_promo_test, y_attr_train, y_attr_test = train_test_split(
            X_scaled, y_promo, y_attr, test_size=test_size, random_state=random_state, stratify=y_promo
        )

        self.imbalance_handler = ImbalanceHandler(random_state=random_state)
        if apply_smote:
            X_promo_train_bal, y_promo_train_bal, smote_report_promo = self.imbalance_handler.resample(
                X_train, y_promo_train, target_label="Promotion"
            )
            X_attr_train_bal, y_attr_train_bal, smote_report_attr = self.imbalance_handler.resample(
                X_train, y_attr_train, target_label="Attrition"
            )
        else:
            X_promo_train_bal, y_promo_train_bal = X_train, y_promo_train
            X_attr_train_bal, y_attr_train_bal = X_train, y_attr_train
            smote_report_promo = {"algorithm": "None (SMOTE Disabled)", "before": {}, "after": {}}
            smote_report_attr = {"algorithm": "None (SMOTE Disabled)", "before": {}, "after": {}}

        # Step E, F, G: Model Training, Evaluation Metrics, Bias-Variance Analysis
        self.promo_trainer = PipelineTrainer(random_state=random_state)
        self.promo_trainer.models["random_forest"].set_params(n_estimators=n_estimators)
        self.promo_trainer.models["gradient_boosting"].set_params(n_estimators=n_estimators)
        promo_results = self.promo_trainer.train_and_evaluate(
            X_promo_train_bal, y_promo_train_bal, X_test, y_promo_test, target_name="Promotion"
        )

        self.attrition_trainer = PipelineTrainer(random_state=random_state)
        self.attrition_trainer.models["random_forest"].set_params(n_estimators=n_estimators)
        self.attrition_trainer.models["gradient_boosting"].set_params(n_estimators=n_estimators)
        attr_results = self.attrition_trainer.train_and_evaluate(
            X_attr_train_bal, y_attr_train_bal, X_test, y_attr_test, target_name="Attrition"
        )

        # Compensation benchmark regressor training
        # Target: monthly_income (non-clipped original)
        clean_income = df["monthly_income"].fillna(df["monthly_income"].median()).values
        self.promo_trainer.train_compensation_model(X_scaled, clean_income)

        # Assemble full educational pipeline visualization payload
        self.pipeline_visualization_data = {
            "metadata": {
                "pipeline_name": "Enterprise Employee Performance & Prediction Pipeline",
                "version": "2.4.0",
                "timestamp": pd.Timestamp.now().isoformat(),
                "test_size": test_size,
                "n_estimators": n_estimators,
                "apply_smote": apply_smote,
                "random_state": random_state
            },
            "step_a_ingestion": {
                "title": "Step 1: Raw Data Ingestion",
                "badge": "Data Acquisition & Profiling",
                "summary": "Ingestion of enterprise HR workforce records containing demographic, compensation, tenure, and performance attributes.",
                "data": ingestion_data
            },
            "step_b_preprocessing": {
                "title": "Step 2: Preprocessing & Data Cleaning",
                "badge": "Imputation, Winsorization, Encoding, Scaling",
                "summary": "Transforms untidy real-world data into standardized high-dimensional numerical feature spaces suitable for mathematical estimators.",
                "data": preproc_report
            },
            "step_c_feature_engineering": {
                "title": "Step 3: Feature Engineering & Selection",
                "badge": "Domain Ratios & Information Gain",
                "summary": "Constructs behavioral ratios and ranks predictor significance via Random Forest Gini impurity and Mutual Information theory.",
                "promotion_features": feature_importance_promo,
                "attrition_features": feature_importance_attrition
            },
            "step_d_imbalance": {
                "title": "Step 4: Class Imbalance Handling",
                "badge": "SMOTE (Synthetic Minority Over-sampling)",
                "summary": "Synthesizes k-nearest neighbor vectors for the minority class to mitigate majority-class accuracy deception.",
                "promotion_smote": smote_report_promo,
                "attrition_smote": smote_report_attr
            },
            "step_e_training": {
                "title": "Step 5: Multi-Model Training",
                "badge": "Linear & Non-Linear Ensembles",
                "summary": "Simultaneously trains Logistic Regression, Random Forest (Bagging), and Gradient Boosting (Boosting) architectures.",
                "models_compared": [
                    {
                        "id": "logistic_regression",
                        "name": "Logistic Regression (L2 Regularized)",
                        "type": "Linear / Parametric Baseline",
                        "advantages": "High interpretability, mathematically stable, fast inference",
                        "use_case": "Provides calibrated baseline probability odds"
                    },
                    {
                        "id": "random_forest",
                        "name": "Random Forest Classifier",
                        "type": "Ensemble (Bagging / Bootstrap Aggregation)",
                        "advantages": "Reduces variance, immune to multi-collinearity, handles non-linearities",
                        "use_case": "Non-linear decision surfaces across heterogeneous attributes"
                    },
                    {
                        "id": "gradient_boosting",
                        "name": "Gradient Boosting Classifier",
                        "type": "Ensemble (Sequential Gradient Boosting)",
                        "advantages": "Minimizes empirical bias sequentially, highest discriminative accuracy",
                        "use_case": "Optimal for complex multivariate HR interactions"
                    }
                ]
            },
            "step_f_evaluation": {
                "title": "Step 6: Evaluation Metrics & Confusion Matrices",
                "badge": "Precision, Recall, F1, ROC-AUC, Error Matrix",
                "summary": "Rigorous test-set verification evaluating Type I (False Positive) and Type II (False Negative) trade-offs in talent management.",
                "promotion_metrics": promo_results["evaluation"],
                "attrition_metrics": attr_results["evaluation"]
            },
            "step_g_bias_variance": {
                "title": "Step 7: Bias-Variance Tradeoff Analysis",
                "badge": "Generalization & Learning Curves",
                "summary": "Diagnoses underfitting vs overfitting by contrasting training loss, test loss, cross-validation variance, and sample complexity.",
                "promotion_bias_variance": promo_results["bias_variance"],
                "attrition_bias_variance": attr_results["bias_variance"]
            },
            "step_h_inference": {
                "title": "Step 8: Final Inference & Explainability (XAI)",
                "badge": "SHAP-style Feature Impact & Recommendations",
                "summary": "Transforms individual employee inputs into calibrated probabilities, positive catalysts, risk drivers, and actionable growth paths."
            }
        }

    def predict_employee(self, employee_dict: Dict[str, Any], analysis_type: str = "all") -> Dict[str, Any]:
        """Runs an individual employee profile through the trained pipeline."""
        if not self.is_initialized:
            self.initialize()

        # Step 1: Vectorize through fitted preprocessor
        feature_vector = self.preprocessor.transform_single(employee_dict)
        feature_names = self.preprocessor.feature_columns

        # Get best fitted models
        best_promo_model = self.promo_trainer.fitted_models.get(
            self.promo_trainer.best_model_name, list(self.promo_trainer.fitted_models.values())[0]
        )
        best_attr_model = self.attrition_trainer.fitted_models.get(
            self.attrition_trainer.best_model_name, list(self.attrition_trainer.fitted_models.values())[0]
        )

        results = {}

        # 1. Promotion Analysis
        if analysis_type in ["all", "promotion"]:
            results["promotion"] = PredictionExplainer.explain_promotion(
                best_promo_model, feature_vector, feature_names, employee_dict
            )

        # 2. Attrition Risk Analysis
        if analysis_type in ["all", "attrition"]:
            results["attrition"] = PredictionExplainer.explain_attrition(
                best_attr_model, feature_vector, feature_names, employee_dict
            )

        # 3. Overall Performance Score & Ranking
        if analysis_type in ["all", "performance"]:
            results["performance"] = PredictionExplainer.explain_performance(
                employee_dict, {}
            )

        # 4. Skill Gap / Training Recommendation
        if analysis_type in ["all", "skill_gap"]:
            results["skill_gap"] = PredictionExplainer.explain_skill_gap(
                employee_dict
            )

        # 5. Compensation Fairness Analysis
        if analysis_type in ["all", "compensation"]:
            predicted_income = self.promo_trainer.predict_compensation(feature_vector)
            results["compensation"] = PredictionExplainer.explain_compensation_fairness(
                employee_dict, predicted_income
            )

        return results

    def get_pipeline_visualization_data(self) -> Dict[str, Any]:
        """Returns comprehensive JSON for the visualizer page."""
        if not self.is_initialized:
            self.initialize()
        return self.pipeline_visualization_data

    def retrain_pipeline(self, test_size: float = 0.2, n_estimators: int = 100, apply_smote: bool = True, random_state: int = 42) -> Dict[str, Any]:
        """Allows dynamic experimentation and re-training from the web UI."""
        self._fit_pipeline(test_size=test_size, n_estimators=n_estimators, apply_smote=apply_smote, random_state=random_state)
        return self.pipeline_visualization_data

# Global Singleton Instance
pipeline_manager = PipelineManager()

