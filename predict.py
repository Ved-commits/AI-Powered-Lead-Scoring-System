import pandas as pd
from joblib import load

def load_model(path: str = "models/model.joblib"):
    return load(path)

def score_leads(model, df: pd.DataFrame) -> pd.DataFrame:
    features = ["industry","lead_source","region","employees","pages_visited","emails_opened","last_contact_days"]
    probs = model.predict_proba(df[features])[:,1]
    out = df.copy()
    out["score"] = probs
    out = out.sort_values("score", ascending=False).reset_index(drop=True)
    out["priority"] = pd.qcut(out["score"], q=5, labels=["Very Low","Low","Medium","High","Very High"])
    return out
