# UK Property Market Analytics & Price Estimator

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)

An end-to-end data pipeline, SQL analytics suite, and machine learning model predicting residential real estate values across England and Wales using official HM Land Registry data.

---

## Live Demo
> **Interactive Web App:** [Link to Streamlit Community Cloud app here]

---

## Architecture Overview

```text
HM Land Registry (Raw CSV) 
   │
   ▼
DuckDB Pipeline (Schema Validation & Aggregations)
   │
   ├──► SQL Analytics (Postcode growth rates, transaction volumes)
   │
   └──► Feature Engineering & Training (XGBoost Regressor)
           │
           ▼
     Streamlit Dashboard (Interactive price evaluation & filters)