import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ----------------------------
# Load trained model
# ----------------------------
model = joblib.load("fraud_model.pkl")
print("ML model loaded ✅")

# ----------------------------
# Load Kaggle dataset
# ----------------------------
df = pd.read_csv("data/ethereum_fraud.csv")
df.columns = df.columns.str.strip()

feature_cols = [c for c in df.columns if c not in
                ["Unnamed: 0", "Index", "Address", "FLAG",
                 "ERC20 most sent token type", "ERC20_most_rec_token_type"]]

X = df.reindex(columns=model.feature_names_in_, fill_value=0)

y_true = df["FLAG"]
X = X.fillna(0)
X = X.reindex(columns=model.feature_names_in_, fill_value=0)

# ----------------------------
# Predict fraud probabilities
# ----------------------------
y_pred_prob = model.predict_proba(X)[:, 1]

# ----------------------------
# Test multiple thresholds
# ----------------------------
thresholds = [0.45, 0.50, 0.55, 0.60, 0.65]
print("\nThreshold analysis:")

for t in thresholds:
    y_pred = (y_pred_prob >= t).astype(int)
    accuracy = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    incorrect = (y_pred != y_true).sum()
    print(f"\nThreshold: {t:.2f}")
    print(f"Accuracy: {accuracy:.4f}, Incorrect predictions: {incorrect}")
    print("Confusion Matrix:")
    print(cm)

# ----------------------------
# Optional: show misclassified rows at best threshold
# ----------------------------
best_threshold = 0.50  # choose based on analysis
y_pred_best = (y_pred_prob >= best_threshold).astype(int)
comparison = pd.DataFrame({
    "Address": df["Address"],
    "Actual_FLAG": y_true,
    "Predicted_FLAG": y_pred_best,
    "Fraud_Prob": y_pred_prob
})
comparison["Correct"] = comparison["Actual_FLAG"] == comparison["Predicted_FLAG"]

incorrect_rows = comparison[comparison["Correct"] == False]
print(f"\nTotal incorrect predictions at threshold {best_threshold}: {len(incorrect_rows)}")
if len(incorrect_rows) > 0:
    print("\nSome incorrect predictions:")
    print(incorrect_rows.head(10))
