import os
import io
import pandas as pd
import streamlit as st
import joblib
from models.predict import load_model, score_leads
from utils.emailer import send_email
from models.train import build_pipeline
from joblib import dump

st.set_page_config(page_title="AI Lead Scorer", page_icon="📈", layout="wide")

st.title("📈 AI-Powered Lead Scoring & Prioritization")
st.caption("Demo project aligned with LeadSquared SDR workflows — lead intake, scoring, prioritization, and follow-up suggestions.")

# Sidebar
with st.sidebar:
    st.header("Model")
    model = joblib.load("models/model.joblib")

    model_exists = os.path.exists(model_path)
    if model_exists:
        st.success("Model found: models/model.joblib")
        model = load_model(model_path)
    else:
        st.warning("No trained model found. Train from sample or your data.")
        model = None

    st.markdown("---")
    st.header("Quick Actions")
    if st.button("Train on sample dataset"):
        from models.train import main as train_main
        with st.spinner("Training on sample data..."):
            train_main()
        st.success("Training complete. Reload the page to use the trained model.")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["Upload Leads", "Score & Prioritize", "Analyze & Visualize", "Automation"])

with tab1:
    st.subheader("Upload leads CSV")
    st.write("Columns expected: industry, lead_source, region, employees, pages_visited, emails_opened, last_contact_days (others will be kept but not used for modeling).")
    sample_dl = st.download_button("Download sample CSV", data=open("data/leads_sample.csv","rb"), file_name="leads_sample.csv", mime="text/csv")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state["uploaded_df"] = df
        st.success(f"Uploaded {df.shape[0]} rows.")
        st.dataframe(df.head())

with tab2:
    st.subheader("Score & Prioritize")
    df = st.session_state.get("uploaded_df")
    if df is None:
        st.info("Upload a CSV in the 'Upload Leads' tab or train a model with the sidebar.")
    else:
        # If no model, quick-train on uploaded data (requires 'converted' column)
        if model is None:
            if "converted" in df.columns:
                st.warning("No model found. You can quick-train a model on the uploaded data since it contains the target 'converted'.")
                if st.button("Quick-train model on uploaded data"):
                    pipe = build_pipeline()
                    features = ["industry","lead_source","region","employees","pages_visited","emails_opened","last_contact_days"]
                    pipe.fit(df[features], df["converted"])
                    dump(pipe, "models/model.joblib")
                    st.success("Quick training done. Reload the page to load the model.")
            else:
                st.error("No model available. Train a model from the sidebar or upload data with a 'converted' column to quick-train.")
        else:
            scored = score_leads(model, df.copy())
            st.session_state["scored_df"] = scored
            st.success("Scoring complete.")
            st.dataframe(scored.head(30))

            st.download_button(
                "Download scored leads CSV",
                data=scored.to_csv(index=False),
                file_name="scored_leads.csv",
                mime="text/csv"
            )

with tab3:
    st.subheader("Analyze & Visualize")
    scored = st.session_state.get("scored_df")
    if scored is None:
        st.info("Score some leads first in the previous tab.")
    else:
        st.write("Top 20 leads by score:")
        st.dataframe(scored.head(20)[["name","email","company","score","priority"]])
        st.write("Distribution of lead priority:")
        counts = scored["priority"].value_counts().reindex(["Very High","High","Medium","Low","Very Low"]).fillna(0)
        import matplotlib.pyplot as plt
        fig = plt.figure()
        counts.plot(kind="bar")
        st.pyplot(fig)

with tab4:
    st.subheader("Automation (Email)")
    scored = st.session_state.get("scored_df")
    if scored is None:
        st.info("Score some leads first in the previous tab.")
    else:
        st.write("Send a simple intro email to top leads (simulation). Configure SMTP via .env to actually send.")
        k = st.slider("How many top leads?", min_value=1, max_value=20, value=5)
        template = st.text_area("Email template", value=(
            "Hi {name},\n\n"
            "I came across {company} and thought LeadSquared could help automate your lead management and increase conversions.\n"
            "If you're open to it, I'd love to schedule a quick 15-minute call to share relevant use-cases for {industry}.\n\n"
            "Best,\nVedant"
        ), height=160)
        to_send = scored.head(k)[["name","email","company","industry"]]

        if st.button(f"Send to top {k} leads"):
            success = 0
            for _, row in to_send.iterrows():
                body = template.format(**row.to_dict())
                ok = send_email(row["email"], "Quick idea for your team", body)
                success += int(ok)
            if success == 0:
                st.warning("No emails sent. Configure SMTP in .env or treat this as a simulation.")
            else:
                st.success(f"Emails sent: {success}")
