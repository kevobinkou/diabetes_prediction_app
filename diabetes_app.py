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
import bcrypt

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
        return mysql.connector.connect(**db_config)
    except Error as e:
        st.error(f"❌ DB connection failed: {e}")
        return None

# ----------------- Authentication -----------------
def register():
    st.subheader("📝 Register")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            try:
                cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed_pw))
                conn.commit()
                st.success("Registration successful! You can now log in.")
            except mysql.connector.IntegrityError:
                st.error("Email already exists.")
            cursor.close()
            conn.close()

def reset_password():
    st.subheader("🔄 Reset Password")
    email = st.text_input("Email for Reset")
    new_password = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_pw, email))
            conn.commit()
            if cursor.rowcount:
                st.success("Password reset successful!")
            else:
                st.error("Email not found.")
            cursor.close()
            conn.close()

def login():
    with st.sidebar:
        st.header("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login")

        if login_btn:
            conn = get_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = email
                    st.session_state["role"] = user["role"]
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.markdown("---")
        if st.button("New user? Register"):
            st.session_state["registering"] = True
            st.rerun()
        if st.button("Forgot password?"):
            st.session_state["resetting"] = True
            st.rerun()

# ----------------- Save to DB -----------------
def save_prediction(data):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO diabetes_predictions 
        (name, age, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, prediction, prediction_confidence)
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
            st.info(result_text)
            st.write(f"**Confidence:** {confidence * 100:.2f}%")

            save_prediction((name, age, pregnancies, glucose, bp, skin, insulin, bmi, pedigree, int(prediction), float(confidence)))

# ----------------- Admin View -----------------
def admin_dashboard():
    st.title("📊 Admin Dashboard")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM diabetes_predictions ORDER BY id DESC", conn)
        st.dataframe(df)

        pred_counts = df["prediction"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(pred_counts, labels=["No Diabetes", "Diabetes"], autopct="%1.1f%%", colors=["#00cc66", "#ff6666"])
        ax.set_title("Prediction Distribution")
        st.pyplot(fig)
        conn.close()

# ----------------- Main -----------------
def main():
    if "logged_in" not in st.session_state:
        if st.session_state.get("registering"):
            register()
        elif st.session_state.get("resetting"):
            reset_password()
        else:
            login()
    else:
        st.sidebar.success(f"Welcome, {st.session_state['username']}!")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        if st.session_state["role"] == "admin":
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()
