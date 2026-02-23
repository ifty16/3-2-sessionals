import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
# any scikit-learn estimator will be used as the base learner (to be provided)
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import xgboost as xgb
import random
from scipy import stats

# Reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)

set_seed(42)

# TODO: Load the dataset




# TODO: Separate features (X) and target (y)



# TODO: Train-test split (80%-20%)




# TODO: Scale the features if needed




# -------------------- Base Learner --------------------

# TODO: Train the base learner and compute the accuracy




# -------------------- bagging/stacking/adaboost etc. with the base learner --------------------




# -------------------- XGBoost --------------------

# TODO: Experiment XGBoost with different combinations of hyperparameters (n_estimators, max_depth, learning_rate etc).


# TODO: Train and predict with each combination
# Find the worst(Lowest possible XGBoost accuracy) and best(Highest possible XGBoost accuracy) XGBoost configurations




# -------------------- Final Output --------------------

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Base Learner Accuracy: {round(lr_acc, 4)}")
print(f"Bagging/Stacking/Adaboost with base learner Accuracy: {round(bagging_acc, 4)}")
print("-" * 60)
print(f"XGBoost Worst Accuracy: {round(xgb_poor_acc, 4)}")
print(f"XGBoost Best Accuracy: {round(xgb_best_acc, 4)}")
print("=" * 60)