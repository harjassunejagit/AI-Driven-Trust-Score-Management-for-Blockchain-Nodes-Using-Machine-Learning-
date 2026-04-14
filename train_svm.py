import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/ethereum_fraud.csv")
df.columns = df.columns.str.strip()

y = df["FLAG"]

feature_cols = [c for c in df.columns if c not in [
    "FLAG","Unnamed: 0","Index","Address",
    "ERC20 most sent token type",
    "ERC20_most_rec_token_type"
]]

X = df[feature_cols].fillna(0)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="rbf"))
])

model.fit(X_train, y_train)
preds = model.predict(X_test)

print("SVM Accuracy:", accuracy_score(y_test, preds))
