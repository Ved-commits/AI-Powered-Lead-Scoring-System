import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression
from joblib import dump

DATA_PATH = os.getenv("DATA_PATH", "data/leads_sample.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.joblib")

def build_pipeline():
    categorical = ["industry", "lead_source", "region"]
    numeric = ["employees", "pages_visited", "emails_opened", "last_contact_days"]

    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", "passthrough", numeric),
        ]
    )
    clf = LogisticRegression(max_iter=200)
    pipe = Pipeline(steps=[("pre", pre), ("clf", clf)])
    return pipe

def main():
    df = pd.read_csv(DATA_PATH)
    features = ["industry","lead_source","region","employees","pages_visited","emails_opened","last_contact_days"]
    X = df[features]
    y = df["converted"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    # Evaluate
    y_prob = pipe.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, y_prob)
    print(f"AUC: {auc:.3f}")
    print(classification_report(y_test, (y_prob>0.5).astype(int)))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    dump(pipe, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    main()
