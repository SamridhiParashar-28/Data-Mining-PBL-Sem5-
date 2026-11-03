import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier

class FeatureEngineer:
    """
    Feature Engineering & Feature Selection Module.
    1. Creates high-yield domain-specific behavioral and organizational features.
    2. Ranks feature importance using Information Gain / Mutual Information and Tree-based Gini Impurity.
    3. Provides detailed educational context on feature selection.
    """

    @staticmethod
    def derive_features(df_input: pd.DataFrame) -> pd.DataFrame:
        """Derives advanced HR analytics features from base attributes."""
        df = df_input.copy()
        
        # 1. Tenure to Age ratio (career loyalty / mobility)
        df["tenure_to_age_ratio"] = (df["years_at_company"] / np.maximum(df["age"] - 18, 1)).round(3)
        
        # 2. Role Stability (time in role vs time at company)
        df["role_stability"] = (df["years_in_current_role"] / np.maximum(df["years_at_company"] + 1, 1)).round(3)
        
        # 3. Income per Experience Year (compensation efficiency)
        df["income_per_year_exp"] = (df["monthly_income"] / np.maximum(df["total_working_years"] + 1, 1)).round(2)
        
        # 4. Burnout Risk Index (combining overtime, poor work-life balance, high project count)
        ot_flag = (df["overtime"] == "Yes").astype(float)
        wlb_deficit = np.maximum(5 - df["work_life_balance"], 0)
        df["burnout_index"] = (ot_flag * 1.5 + wlb_deficit * 0.4 + (df["projects_completed"] / 10.0)).round(3)
        
        # 5. Growth Momentum (combines training effort and performance)
        df["growth_momentum"] = ((df["training_hours_last_year"] / 35.0) * (df["performance_rating"] / 3.5)).round(3)
        
        return df

    @staticmethod
    def compute_feature_importances(
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        target_name: str = "promoted"
    ) -> Dict[str, Any]:
        """
        Computes Random Forest Gini importance and Mutual Information Gain scores
        for the engineered feature matrix against a specified target.
        """
        # Fit a quick Random Forest to measure feature importance
        rf = RandomForestClassifier(n_estimators=75, max_depth=6, random_state=42)
        rf.fit(X, y)
        importances = rf.feature_importances_
        
        # Also compute Mutual Information Gain (Information Theory)
        mi_scores = mutual_info_classif(X, y, random_state=42)
        
        # Normalize and rank
        combined_scores = []
        for name, rf_score, mi_score in zip(feature_names, importances, mi_scores):
            combined_scores.append({
                "feature": name,
                "clean_name": name.replace("_", " ").title(),
                "rf_importance": round(float(rf_score), 4),
                "mutual_info": round(float(mi_score), 4),
                "relative_weight_pct": round(float(rf_score) * 100, 2)
            })
            
        combined_scores.sort(key=lambda x: x["rf_importance"], reverse=True)
        
        return {
            "target": target_name,
            "top_features": combined_scores[:12],
            "total_features_analyzed": len(feature_names),
            "explanation": (
                f"Feature ranking for '{target_name}' using Random Forest Gini impurity reduction "
                f"and Information Gain (Mutual Information). The top features possess the greatest "
                f"discriminative power in distinguishing positive from negative outcomes."
            )
        }

