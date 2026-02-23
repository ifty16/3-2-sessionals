import numpy as np
import pandas as pd
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# --- 1. DATA LOADING ---
# Load the dataset from the path
train = pd.read_csv("/kaggle/input/creditcardfraud/creditcard.csv") 

# --- 2. PRE-PROCESSING & EXPLORATION ---
label_encoder = LabelEncoder()
scaler = StandardScaler()

# Convert text/object columns to numbers; XGBoost requires numeric input
# Alternative: Newer XGBoost versions allow 'enable_categorical=True' if using Pandas category type
df = train.apply(lambda x: label_encoder.fit_transform(x) if x.dtype == 'O' else x)

# Scale features to mean=0, std=1
# Alternative: This is optional; Cheat Sheet notes "Scaling: Not required for tree-based models"
trainup = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

# Visualize relationships to identify redundant features
cov_matrix = abs(trainup.cov())
plt.figure(figsize=(20, 20))
sns.heatmap(cov_matrix, annot=True, cmap='Blues', fmt='.2f', linewidths=.5)
plt.show()

# --- 3. FEATURE SELECTION & SPLITTING ---
# Drop features that are redundant or low importance
df = df.drop(['Time', 'V13', 'V15', 'V22', 'V23', 'V24','V25','V26','V28', 'Amount' ], axis=1)

# Separate features (X) and target (Y)
X = df.drop(['Class'], axis=1)
Y = df['Class']

# Re-scaling X for consistency (even if optional for XGBoost)
X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# --- 4. MODEL INITIALIZATION ---
# Initialize Classifier with specific 'Brakes' and 'Engine' params
# Alternative: For regression, use 'XGBRegressor' and 'reg:squarederror' objective
model = xgb.XGBClassifier(
    learning_rate=0.1,      # Step size shrinkage (eta)
    max_depth=5,            # Max tree depth; higher = more overfitting
    min_child_weight=3,     # Min sum of instance weight (hessian) needed in a child
    subsample=0.8,          # % of rows used per tree
    colsample_bytree=0.9,   # % of columns used per tree
    n_estimators=500,       # Number of trees to grow
    objective='binary:logistic' # Output probabilities for 2 classes
)

# --- 5. VALIDATION (K-FOLD) ---
# Check model stability across 5 different data splits
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_results = cross_val_score(model, X, Y, cv=kf, scoring='accuracy')
print("Average Accuracy:", cv_results.mean())

# --- 6. TRAINING & EVALUATION ---
# Split into Train/Test; 'stratify' is key for imbalanced fraud data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, stratify=Y, random_state=42)

# Train the model
# Alternative: Use 'early_stopping_rounds' inside fit() to prevent overfitting
model.fit(X_train, y_train)

# Predict on unseen data
prediction = model.predict(X_test)

# Display Confusion Matrix
cm = metrics.confusion_matrix(y_test, prediction)
cm_dis = metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=df['Class'].unique())
cm_dis.plot()
plt.show()

# Detailed metrics (Precision, Recall, F1)
print('Classification Report:\n', metrics.classification_report(y_test, prediction))

# --- 7. INTERPRETABILITY ---
# View which features drove the model's decisions
# Alternative: Use importance_type='weight' to see frequency
xgb.plot_importance(model, importance_type='gain')
plt.show()