# 🩺 DiaHeart Assistant: AI-Powered Diabetes & Cardiovascular Risk Intelligence

DiaHeart Assistant is a professional, high-performance web application designed to help individuals assess their risk levels for Diabetes and Cardiovascular Disease (CVD). By utilizing pre-trained Machine Learning (Random Forest) models and clinical datasets, the application evaluates physiological factors, medical history, and blood parameters to deliver predictive insights, empathy-driven lifestyle recommendations, and secure medical reports.

---

## 🚀 Key Features

* **Dual AI Prediction Engines**:
  * **Diabetes Predictor**: Evaluates metrics such as Glucose levels, BMI, Systolic/Diastolic Blood Pressure, and family history.
  * **Cardiovascular (Heart) Predictor**: Evaluates parameters including Cholesterol, resting heart rate, prevalent hypertension, smoking habits, and medication history.
* **Empathy-Driven Recommendations**: Integrates a wellness engine that generates tailored lifestyle advice, nutritional focus areas, and clinical consultation checklists based on whether the risk is Low, Medium, or High.
* **Secure User Authentication**: Built-in registration, password hashing (SHA-256), and secure session management using a local SQLite3 database.
* **Personal Diagnostic Dashboard**: Visualizes previous health assessment outcomes using interactive **Plotly** charts (pie charts for risk breakdown and histograms for test frequency).
* **One-Click PDF Report Export**: Dynamically compiles assessment details and outputs a downloadable, professionally formatted PDF clinical summary report.
* **Educational Knowledge Hub**: A dedicated section displaying curated videos regarding heart disease, diabetes mechanics, and the role of AI in medicine.
* **Conversational AI Companion**: Integrates a live **Botpress Chatbot** widget inside the authenticated platform for interactive guidance.
* **Premium Dark Mode UI**: Customized using a custom SVG brand assets logo, sleek slate dark colors (`#0f172a`), interactive card animations, and responsive web elements.

---

## 🛠️ Technology Stack

* **Frontend Framework**: [Streamlit](https://streamlit.io/) (v1.22.0+ recommended)
* **Programming Language**: [Python](https://www.python.org/) (v3.10+ recommended)
* **Machine Learning & Data Processing**: 
  * `scikit-learn` & `joblib` (Random Forest classifiers)
  * `pandas` & `numpy` (Scientific data manipulation)
* **Database**: SQLite3 (Local file-based system)
* **Data Visualization**: [Plotly Express](https://plotly.com/python/)
* **Document Generation**: `fpdf` (PDF exports)
* **Chatbot Platform**: Botpress Webchat Integration

---

## 📁 Repository Structure

```filepath
diaheart/
├── .streamlit/
│   ├── config.toml           # Theme and styling configuration (Slate Dark)
│   └── secrets.toml          # Local secrets & API key configs (Google API Key placeholder)
├── CVD_model.pkl             # Pre-trained Cardiovascular Disease classification model
├── diabetes_model.pkl        # Pre-trained Diabetes classification model
├── cvd_median.pkl            # Median normalization values for CVD prediction inputs
├── app.py                    # Main Streamlit web application & authentication router
├── recommendation_engine.py  # Empathy-driven wellness recommendation processor
├── users.db                  # Local SQLite3 database (holds user credentials & logs)
└── README.md                 # Project documentation
```

---

## ⚙️ Installation & Setup

Follow these steps to set up and run the DiaHeart Assistant locally:

### 1. Prerequisites
Ensure you have **Python 3.10 or higher** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/diaheart-assistant.git
cd diaheart-assistant
```

### 3. Install Dependencies
Install all required libraries using `pip`:
```bash
pip install streamlit pandas numpy joblib scikit-learn plotly fpdf
```

### 4. Run the Streamlit Application
Launch the app locally:
```bash
streamlit run app.py
```
This command will launch the development server and output the local URL (typically `http://localhost:8501`).

---

## 🔒 Security & Version Control

To avoid uploading sensitive user credentials or local database records to your public GitHub repository, it is **highly recommended** to configure a `.gitignore` file before pushing. 

Create a `.gitignore` file in the root of the project with the following lines:
```text
# Cache and compilation outputs
__pycache__/
*.pyc

# Local databases
users.db

# User specific configuration/secrets
.streamlit/secrets.toml
```

---

## 👥 Project Developers

Developed with care by:
* **Alisha Amjad**
* **Fatima Munir**

---

## ⚠️ Medical Disclaimer

> [!IMPORTANT]
> This application is built as an educational AI healthcare project. The system does not provide medical diagnoses or replace professional clinical consultations. Always seek the advice of a qualified physician or healthcare provider regarding any medical condition.
