import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ----------------------------
# Load trained model & features
# ----------------------------
model = joblib.load("fraud_model.pkl")
feature_cols = joblib.load("feature_cols.pkl")  # ✅ FIXED

# ----------------------------
# Load Kaggle dataset
# ----------------------------
df = pd.read_csv("data/ethereum_fraud.csv")
df.columns = df.columns.str.strip()

X = df.reindex(columns=feature_cols, fill_value=0)
y = df["FLAG"]

# ----------------------------
# Predict & evaluate
# ----------------------------
y_pred = model.predict(X)

print("Accuracy:", accuracy_score(y, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y, y_pred))
print("\nClassification Report:")
print(classification_report(y, y_pred))
