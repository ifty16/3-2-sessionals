import numpy as np
import pandas as pd
import os
import re
import warnings
train=pd.read_csv("/kaggle/input/mushroom-classification/mushrooms.csv")
train

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
label_encoder = LabelEncoder()
scaler= StandardScaler()
df = train.apply(lambda x: label_encoder.fit_transform(x) if x.dtype == 'O' else x)
trainup = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
cov_matrix = abs(trainup.cov())
plt.figure(figsize=(20, 20))
sns.heatmap(cov_matrix, annot=True, cmap='Greens', fmt='.2f', linewidths=.5)
plt.title('Covariance Matrix Heatmap')
plt.show()

df=df.drop(['veil-type' ], axis=1)
X_train=df.drop(['class'], axis=1)
Y_train=df['class']
X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import KFold, cross_val_score
model = AdaBoostClassifier()
kf = KFold(n_splits=4, shuffle=True, random_state=42)
cv_results = cross_val_score(model, X_train, Y_train, cv=kf, scoring='accuracy')
accuracy_values = cv_results
average_accuracy = cv_results.mean()

print("Accuracy for each fold:", accuracy_values)
print("Average Accuracy across all folds:", average_accuracy)