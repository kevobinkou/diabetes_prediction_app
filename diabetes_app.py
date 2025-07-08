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
from mysql.connector import Error
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# ----------------- Load Trained Model -----------------
model = joblib.load("diabetes_model.joblib")

# ----------------- Secrets for DB -----------------
db_config = {
    "host": st.secrets["db_host"],
    "user": st.secrets["db_user"],
    "password": st.secrets["db_password"],
    "database": st.secrets["db_name"],
    "port": int(st.secrets["db_port"])
}

# ----------------- DB Connection -----------------
def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        st.error(f"❌ DB connection failed: {e}")
        return None

# ----------------- Auth -----------------
users = {
    "admin": "admin123",
    "user1": "pass1",
    "user2": "pass2"
}

def login():
    with st.sidebar:
        st.header("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# ----------------- Save to DB -----------------
def save_prediction(data):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO diabetes_predictions (name, age, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, prediction, prediction_confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, data)
        conn.commit()
        cursor.close()
        conn.close()

# ----------------- User View -----------------
def user_dashboard():
    st.title("🩺 Diabetes Risk Prediction")

    with st.form("prediction_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Age", 1, 120)
        pregnancies = st.number_input("Pregnancies", 0, 20)
        glucose = st.number_input("Glucose Level", 0.0, 300.0)
        bp = st.number_input("Blood Pressure", 0.0, 200.0)
        skin = st.number_input("Skin Thickness", 0.0, 100.0)
        insulin = st.number_input("Insulin Level", 0.0, 900.0)
        bmi = st.number_input("BMI", 0.0, 80.0)
        pedigree = st.number_input("Diabetes Pedigree Function", 0.0, 2.5)

        submit = st.form_submit_button("Predict")

        if submit:
            features = np.array([[pregnancies, glucose, bp, skin, insulin, bmi, pedigree, age]])
            prediction = model.predict(features)[0]
            confidence = model.predict_proba(features)[0][prediction]

            result_text = "✅ You are less likely to have diabetes." if prediction == 0 else "⚠️ You may be at risk. Please consult a doctor."
            st.subheader("Prediction Result")
            st.info(f"{result_text}")
            st.write(f"**Confidence:** {confidence * 100:.2f}%")

            # Save result
            save_prediction((name, age, pregnancies, glucose, bp, skin, insulin, bmi, pedigree, int(prediction), float(confidence)))

# ----------------- Admin View -----------------
def admin_dashboard():
    st.title("📊 Admin Dashboard")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM diabetes_predictions ORDER BY date DESC", conn)
        st.dataframe(df)

        # Plot
        pred_counts = df["prediction"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pred_counts, labels=["No Diabetes", "Diabetes"], autopct="%1.1f%%", colors=["#00cc66", "#ff6666"])
        ax.set_title("Prediction Distribution")
        st.pyplot(fig)

        conn.close()

# ----------------- Main -----------------
if "logged_in" not in st.session_state:
    login()
else:
    st.sidebar.success(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state["username"] == "admin":
        admin_dashboard()
    else:
        user_dashboard()
