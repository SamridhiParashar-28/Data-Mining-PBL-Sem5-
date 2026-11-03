import numpy as np
from typing import Tuple, Dict, Any
from imblearn.over_sampling import SMOTE

class ImbalanceHandler:
    """
    Class Imbalance Handling using Synthetic Minority Over-sampling Technique (SMOTE).
    In real-world HR data mining, positive events (Promotion, Attrition) are rare (~15-18%).
    SMOTE synthesizes plausible feature vectors for the minority class along line segments
    connecting k-nearest neighbors, preventing model bias towards the majority class.
    """

    def __init__(self, k_neighbors: int = 5, random_state: int = 42):
        self.k_neighbors = k_neighbors
        self.random_state = random_state
        self.smote = SMOTE(k_neighbors=self.k_neighbors, random_state=self.random_state)

    def resample(self, X: np.ndarray, y: np.ndarray, target_label: str = "Target") -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Applies SMOTE to balance the training dataset.
        Returns resampled (X_res, y_res) and detailed educational statistics.
        """
        unique, counts = np.unique(y, return_counts=True)
        before_dist = dict(zip([int(u) for u in unique], [int(c) for c in counts]))
        total_before = len(y)
        
        # Check if minority count is sufficient for k_neighbors
        min_class_count = min(before_dist.values())
        actual_k = min(self.k_neighbors, max(1, min_class_count - 1))
        
        resampler = SMOTE(k_neighbors=actual_k, random_state=self.random_state)
        X_resampled, y_resampled = resampler.fit_resample(X, y)
        
        unique_after, counts_after = np.unique(y_resampled, return_counts=True)
        after_dist = dict(zip([int(u) for u in unique_after], [int(c) for c in counts_after]))
        total_after = len(y_resampled)
        
        synthetic_created = total_after - total_before
        
        report = {
            "target_label": target_label,
            "algorithm": "SMOTE (Synthetic Minority Over-sampling Technique)",
            "k_neighbors": actual_k,
            "before": {
                "class_0_count": before_dist.get(0, 0),
                "class_1_count": before_dist.get(1, 0),
                "class_0_pct": round((before_dist.get(0, 0) / total_before) * 100, 2),
                "class_1_pct": round((before_dist.get(1, 0) / total_before) * 100, 2),
                "imbalance_ratio": f"1 : {round(before_dist.get(0, 0) / max(1, before_dist.get(1, 0)), 2)}"
            },
            "after": {
                "class_0_count": after_dist.get(0, 0),
                "class_1_count": after_dist.get(1, 0),
                "class_0_pct": round((after_dist.get(0, 0) / total_after) * 100, 2),
                "class_1_pct": round((after_dist.get(1, 0) / total_after) * 100, 2),
                "imbalance_ratio": "1 : 1.00 (Balanced)"
            },
            "synthetic_samples_generated": synthetic_created,
            "educational_note": (
                "Without SMOTE, the classifier would tend to predict the majority class (No Promotion / No Attrition) "
                "to artificially maximize accuracy while failing to detect crucial positive instances. "
                "SMOTE synthesizes authentic minority vectors in high-dimensional feature space, "
                "enabling the decision boundary to generalize without simple duplicate memorization."
            )
        }
        
        return X_resampled, y_resampled, report

