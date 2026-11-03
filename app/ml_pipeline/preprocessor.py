import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.preprocessing import StandardScaler

class DataMiningPreprocessor:
    """
    Comprehensive Data Preprocessing Pipeline implementing standard Data Mining methodologies:
    1. Missing Value Detection & Imputation (Median for numerical, Mode for categorical)
    2. Outlier Detection & Winsorization (IQR rule: Q1 - 1.5*IQR to Q3 + 1.5*IQR)
    3. Categorical Encoding (One-Hot Encoding with tracked dummy columns)
    4. Feature Scaling (Z-Score Standardization: mu=0, sigma=1)
    """

    NUMERICAL_FEATURES = [
        "age", "monthly_income", "years_at_company", "years_in_current_role",
        "years_since_last_promotion", "total_working_years", "performance_rating",
        "projects_completed", "training_hours_last_year", "job_satisfaction",
        "work_life_balance", "environment_satisfaction", "distance_from_home",
        "stock_option_level", "education_level"
    ]

    OUTLIER_CANDIDATES = ["monthly_income", "distance_from_home", "projects_completed"]

    CATEGORICAL_FEATURES = ["department", "job_role", "education_field", "overtime"]

    def __init__(self):
        self.imputation_values = {}
        self.outlier_bounds = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.encoded_feature_names = []
        self.is_fitted = False
        self.preprocessing_report = {}

    def fit_transform(self, df_raw: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Fits preprocessing parameters on raw dataframe and returns scaled feature array and report."""
        df = df_raw.copy()
        report = {
            "initial_shape": df.shape,
            "missing_values": {},
            "outliers_detected": {},
            "encoded_features_count": 0,
            "feature_names": [],
            "scaling_stats": {}
        }

        # Step 1: Missing Value Imputation
        for col in self.NUMERICAL_FEATURES:
            if col in df.columns:
                null_count = int(df[col].isnull().sum())
                median_val = float(df[col].median(skipna=True))
                self.imputation_values[col] = median_val
                df[col] = df[col].fillna(median_val)
                report["missing_values"][col] = {
                    "missing_count": null_count,
                    "imputed_with": "median",
                    "value": round(median_val, 2)
                }

        for col in self.CATEGORICAL_FEATURES:
            if col in df.columns:
                null_count = int(df[col].isnull().sum())
                mode_val = str(df[col].mode()[0])
                self.imputation_values[col] = mode_val
                df[col] = df[col].fillna(mode_val)
                if null_count > 0:
                    report["missing_values"][col] = {
                        "missing_count": null_count,
                        "imputed_with": "mode",
                        "value": mode_val
                    }

        # Step 2: Outlier Handling via IQR Winsorization
        for col in self.OUTLIER_CANDIDATES:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = max(0, q1 - 1.5 * iqr)
                upper_bound = q3 + 1.5 * iqr
                
                outliers_low = (df[col] < lower_bound).sum()
                outliers_high = (df[col] > upper_bound).sum()
                total_outliers = int(outliers_low + outliers_high)
                
                self.outlier_bounds[col] = (lower_bound, upper_bound)
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
                report["outliers_detected"][col] = {
                    "q1": round(float(q1), 2),
                    "q3": round(float(q3), 2),
                    "iqr": round(float(iqr), 2),
                    "lower_bound": round(float(lower_bound), 2),
                    "upper_bound": round(float(upper_bound), 2),
                    "outliers_clipped": total_outliers
                }

        # Step 3: Categorical One-Hot Encoding
        cat_df = pd.get_dummies(df[self.CATEGORICAL_FEATURES], drop_first=False, dtype=float)
        self.encoded_feature_names = list(cat_df.columns)

        # Combine numerical and encoded categorical
        num_df = df[self.NUMERICAL_FEATURES].astype(float)
        X_combined = pd.concat([num_df.reset_index(drop=True), cat_df.reset_index(drop=True)], axis=1)
        self.feature_columns = list(X_combined.columns)

        # Step 4: Feature Scaling (StandardScaler)
        X_scaled = self.scaler.fit_transform(X_combined)

        # Record scaling stats for reporting
        for i, col in enumerate(self.feature_columns):
            report["scaling_stats"][col] = {
                "mean": round(float(self.scaler.mean_[i]), 4),
                "std": round(float(self.scaler.scale_[i]), 4)
            }

        report["final_features_shape"] = X_scaled.shape
        report["encoded_features_count"] = len(self.feature_columns)
        report["feature_names"] = self.feature_columns

        self.is_fitted = True
        self.preprocessing_report = report
        return X_scaled, report

    def transform_single(self, employee_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single employee's dictionary into the exact feature vector for model inference."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet!")

        row_df = pd.DataFrame([employee_dict])

        # Step 1: Imputation
        for col in self.NUMERICAL_FEATURES:
            if col not in row_df.columns or pd.isna(row_df.loc[0, col]):
                row_df[col] = self.imputation_values.get(col, 0.0)
            row_df[col] = float(row_df[col].iloc[0])

        for col in self.CATEGORICAL_FEATURES:
            if col not in row_df.columns or pd.isna(row_df.loc[0, col]):
                row_df[col] = self.imputation_values.get(col, "")
            row_df[col] = str(row_df[col].iloc[0])

        # Step 2: Outlier Clipping
        for col, (lower, upper) in self.outlier_bounds.items():
            if col in row_df.columns:
                row_df[col] = float(np.clip(row_df[col].iloc[0], lower, upper))

        # Step 3: Categorical One-Hot Encoding
        cat_df = pd.get_dummies(row_df[self.CATEGORICAL_FEATURES], drop_first=False, dtype=float)
        # Ensure all encoded columns from training exist
        for col in self.encoded_feature_names:
            if col not in cat_df.columns:
                cat_df[col] = 0.0

        cat_df = cat_df[self.encoded_feature_names]
        num_df = row_df[self.NUMERICAL_FEATURES].astype(float)
        
        combined_df = pd.concat([num_df.reset_index(drop=True), cat_df.reset_index(drop=True)], axis=1)
        combined_df = combined_df[self.feature_columns]

        # Step 4: Scale
        scaled_vec = self.scaler.transform(combined_df)
        return scaled_vec

