# train_model.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

def train_model():
    df = pd.read_csv("data/ethereum_fraud.csv")
    df.columns = df.columns.str.strip()
    
    y = df["FLAG"]
    feature_cols = [c for c in df.columns if c not in ["FLAG","Unnamed: 0","Index","Address",
                                                       "ERC20 most sent token type",
                                                       "ERC20_most_rec_token_type"]]
    X = df[feature_cols].fillna(0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    joblib.dump(model, "fraud_model.pkl")
    joblib.dump(model.feature_names_in_, "model_features.pkl")

    joblib.dump(feature_cols, "feature_cols.pkl")
    print("\nModel and feature columns saved ✅")
