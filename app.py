import streamlit as st
import pandas as pd
import numpy as np
import joblib
import duckdb

st.set_page_config(page_title="UK Property Price Estimator", layout="wide")

st.title("🏡 UK Residential Property Price Estimator")
st.markdown("Estimate fair market values based on official **HM Land Registry** sales data.")

@st.cache_resource
def load_resources():
    model = joblib.load("data/property_model.joblib")
    con = duckdb.connect("data/properties.duckdb", read_only=True)
    postcodes = [row[0] for row in con.execute("""
        SELECT DISTINCT SPLIT_PART(postcode, ' ', 1) as area 
        FROM sales 
        WHERE postcode IS NOT NULL 
        ORDER BY area
    """).fetchall()]
    con.close()
    return model, postcodes

try:
    model, postcodes = load_resources()
except Exception:
    st.error("Please run `python src/model.py` first to generate the trained model.")
    st.stop()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Property Specifications")
    
    postcode_area = st.selectbox("Postcode Outward Area (e.g. SW1, E14, B1)", postcodes)
    
    prop_type_map = {
        "D": "Detached",
        "S": "Semi-Detached",
        "T": "Terraced",
        "F": "Flat / Maisonette"
    }
    prop_type = st.selectbox("Property Type", options=list(prop_type_map.keys()), format_func=lambda x: prop_type_map[x])
    
    is_new = st.radio("Is it a New Build?", options=["N", "Y"], format_func=lambda x: "Yes" if x == "Y" else "No (Established Home)")
    
    tenure = st.radio("Tenure", options=["F", "L"], format_func=lambda x: "Freehold" if x == "F" else "Leasehold")

    predict_btn = st.button("Calculate Valuation", type="primary")

with col2:
    st.subheader("Valuation Summary")
    if predict_btn:
        # Wrap input into a pandas DataFrame matching model training schema
        input_df = pd.DataFrame([{
            "property_type": prop_type,
            "is_new_build": is_new,
            "tenure": tenure,
            "postcode_area": postcode_area
        }])
        
        log_pred = model.predict(input_df)[0]
        pred_price = np.expm1(log_pred)
        
        st.metric(label="Estimated Fair Value", value=f"£{pred_price:,.0f}")
        st.info(f"**Confidence Range:** £{pred_price*0.9:,.0f} — £{pred_price*1.1:,.0f}")
        
        st.markdown("""
        *Estimates are calculated using gradient-boosted trees trained on official HM Land Registry transaction data.*
        """)