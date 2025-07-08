# 🩺 Diabetes Prediction App

A web-based machine learning app built with **Streamlit** that predicts whether a person is likely to have diabetes based on key health indicators.

---

## 🚀 Features

- 🔐 **Role-based Login System** (User & Admin)
- 📊 **Prediction Confidence Display**
- 🧮 **Input Features**: Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree, Age
- 🌐 **Clever Cloud MySQL** database integration
- 📈 **Admin Dashboard**: View and analyze all predictions
- 📱 **Mobile-friendly UI**

---

## 🧠 How It Works

1. The user logs in and enters health metrics.
2. A trained **Decision Tree Classifier** makes a prediction.
3. Results are displayed with confidence scores and saved to a cloud database.

---

## 💻 Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Model**: `DecisionTreeClassifier` from `scikit-learn`
- **Database**: MySQL hosted on Clever Cloud
- **Deployment**: Streamlit Cloud
- **Version Control**: Git & GitHub

---

## 📸 Screenshot

> _Add a screenshot here once deployed_

```markdown
![App Screenshot](screenshot.png)
🔗 Live Demo
Once deployed to Streamlit Cloud, paste your link here:

🌐 Launch the App

🛠️ Setup Instructions (Optional)
bash
Copy
Edit
git clone https://github.com/kevobinkou/diabetes_prediction_app.git
cd diabetes_prediction_app
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run diabetes_app.py
📄 License
MIT License. See LICENSE for details.