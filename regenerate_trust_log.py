# regenerate_trust_log.py
import pandas as pd
import joblib
from datetime import datetime

def regenerate_trust_log():
    # Load dataset
    df = pd.read_csv("data/ethereum_fraud.csv")
    df.columns = df.columns.str.strip()  # remove leading/trailing spaces

    # Load trained model
    model = joblib.load("fraud_model.pkl")

    # Identify model features
    model_features = model.feature_names_in_

    # Ensure only features seen during training are used
    X = df.reindex(columns=model_features, fill_value=0)


    # Actual labels
    y_actual = df["FLAG"]

    # Predict
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]

    # Generate trust log
    rows = []
    for i in range(len(df)):
        trust_score = max(0, 100 - int(probs[i] * 100))
        rows.append({
            "timestamp": datetime.now(),
            "address": df.loc[i, "Address"] if "Address" in df.columns else i,
            "actual_label": int(y_actual.iloc[i]),
            "predicted_label": int(preds[i]),
            "fraud_probability": float(probs[i]),
            "trust_score": trust_score,
            "source": "KAGGLE_ETHEREUM_DATASET"
        })

    trust_log = pd.DataFrame(rows)
    trust_log.to_csv("trust_log.csv", index=False)
    print("trust_log.csv regenerated successfully ✅")
