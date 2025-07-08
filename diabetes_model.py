# ----------------- Page Configuration -----------------
import streamlit as st
st.set_page_config(
    page_title="Diabetes Prediction App",
    layout="centered",
    page_icon="🩺"
)

# ----------------- Imports -----------------
import joblib
import numpy as np
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ----------------- Load Model -----------------
model = joblib.load("diabetes_model.joblib")

# ----------------- DB Connection -----------------
def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["db_host"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        database=st.secrets["db_name"]
    )

# ----------------- Predict Function -----------------
def predict_diabetes(data):
    prediction = model.predict([data])[0]
    proba = model.predict_proba([data])[0]
    return prediction, proba

# ----------------- Insert Prediction -----------------
def insert_prediction(email, role, features, prediction, confidence):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO diabetes_predictions (email, role, pregnancies, glucose, bp, skin_thickness, insulin, bmi, dpf, age, prediction, confidence, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        email, role,
        int(features[0]), int(features[1]), int(features[2]), int(features[3]),
        float(features[4]), float(features[5]), float(features[6]), int(features[7]),
        int(prediction), float(confidence), datetime.now()
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# ----------------- Login System -----------------
def login():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email in st.secrets["users"] and st.secrets["users"][email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.role = st.secrets["users"][email]["role"]
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# ----------------- Prediction Page -----------------
def prediction_page():
    st.title("🩺 Diabetes Prediction")

    pregnancies = st.number_input("Pregnancies", 0, 20)
    glucose = st.number_input("Glucose", 0, 200)
    bp = st.number_input("Blood Pressure", 0, 140)
    skin = st.number_input("Skin Thickness", 0, 100)
    insulin = st.number_input("Insulin", 0.0, 1000.0)
    bmi = st.number_input("BMI", 0.0, 60.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0)
    age = st.number_input("Age", 1, 100)

    if st.button("Predict"):
        features = [pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]
        pred, proba = predict_diabetes(features)
        label = "Diabetic" if pred == 1 else "Not Diabetic"
        confidence = max(proba)

        st.success(f"Prediction: {label} ({confidence*100:.2f}% confidence)")
        insert_prediction(
            st.session_state.email,
            st.session_state.role,
            features,
            pred,
            confidence
        )

# ----------------- Admin Dashboard -----------------
def admin_dashboard():
    st.title("📊 Admin Dashboard - All Predictions")

    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM diabetes_predictions", conn)
    conn.close()

    st.dataframe(df)

    st.subheader("📈 Prediction Distribution")
    fig, ax = plt.subplots()
    df['prediction'].value_counts().plot(kind='bar', color=['green', 'red'], ax=ax)
    ax.set_xticklabels(["Not Diabetic", "Diabetic"], rotation=0)
    ax.set_ylabel("Count")
    st.pyplot(fig)

# ----------------- App Router -----------------
if "logged_in" not in st.session_state:
    login()
else:
    st.sidebar.write(f"Welcome, **{st.session_state.email}**")
    st.sidebar.write(f"Role: `{st.session_state.role}`")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        prediction_page()
