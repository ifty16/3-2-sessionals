import numpy as np
import pandas as pd
import random
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import BaggingClassifier, AdaBoostClassifier, StackingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris # Example for built-in loading

# Reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)

set_seed(42)

# --- TODO: Load the dataset ---
# GENERAL SOLUTION: Load from a CSV or a built-in library
# Alt 1: df = pd.read_csv("data.csv") # Assuming file is in the same local folder
# Alt 2: from sklearn.datasets import load_iris; data = load_iris(); df = pd.DataFrame(data.data, columns=data.feature_names); df['target'] = data.target
df = pd.read_csv("/kaggle/input/creditcardfraud/creditcard.csv") 

# --- TODO: Separate features (X) and target (y) ---
# GENERAL SOLUTION: Assume the last column is the target
# Alt: X = df.iloc[:, :-1]; y = df.iloc[:, -1] # Index-based selection if name is unknown
# Alt: If the target column is named (e.g., 'Class'), you can also do:    y = df['Class']; X = df.drop('Class', axis=1)
X = df.drop(df.columns[-1], axis=1) 
y = df[df.columns[-1]] 

# --- TODO: Train-test split (80%-20%) ---
# GENERAL SOLUTION: Use stratify=y to maintain class balance
# Alt: X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) # Simple split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)

# --- TODO: Scale the features if needed ---
# GENERAL SOLUTION: Fit on train, transform on both || fit means compute mean/std on train only || transform means scaling
# Alt: No scaling needed if only using XGBoost
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------- Base Learner --------------------

# --- TODO: Train the base learner and compute accuracy ---
# GENERAL SOLUTION: Logistic Regression is standard
# Alt: from sklearn.tree import DecisionTreeClassifier; base_model = DecisionTreeClassifier()
base_model = LogisticRegression(max_iter=1000)
base_model.fit(X_train_scaled, y_train)
lr_acc = accuracy_score(y_test, base_model.predict(X_test_scaled))

# -------------------- Bagging/Stacking/AdaBoost --------------------

# --- TODO: Implement alternative ensemble with base learner ---
# GENERAL SOLUTION: AdaBoost (Boosting reduces bias)
# Alt 1: ensemble = BaggingClassifier(estimator=base_model, n_estimators=10) # Parallel (Reduces variance)
# Alt 2: ensemble = StackingClassifier(estimators=[('lr', base_model)], final_estimator=LogisticRegression())
ensemble = AdaBoostClassifier(estimator=base_model, n_estimators=50, algorithm='SAMME')
ensemble.fit(X_train_scaled, y_train)
bagging_acc = accuracy_score(y_test, ensemble.predict(X_test_scaled))

# -------------------- XGBoost --------------------

# --- TODO: Experiment with hyperparameter combinations ---
# Using Section 7 of Cheat Sheet: "Power" vs "Control"
configs = [
    {'n_estimators': 10, 'max_depth': 2, 'learning_rate': 0.01},  # "Worst": Weak engine, high brakes
    {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1}  # "Best": Balanced power
]

results = []
for config in configs:
    # Alt: Use objective='multi:softprob' if you have more than 2 classes
    xgb_model = xgb.XGBClassifier(**config, objective='binary:logistic', random_state=42)
    
    # Alt: Use early_stopping_rounds=10 within fit() to prevent overfitting
    xgb_model.fit(X_train, y_train) 
    
    preds = xgb_model.predict(X_test)
    results.append(accuracy_score(y_test, preds))

xgb_poor_acc = min(results)
xgb_best_acc = max(results)

# -------------------- Final Output --------------------
print("\n" + "="*60)
print("FINAL RESULTS")
print(f"Base Learner Accuracy: {round(lr_acc, 4)}")
print(f"Ensemble (AdaBoost) Accuracy: {round(bagging_acc, 4)}")
print(f"XGBoost Worst: {round(xgb_poor_acc, 4)} | XGBoost Best: {round(xgb_best_acc, 4)}")
print("="*60)