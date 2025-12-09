# Healthcare Monitoring AI Agent – Medication & Wellness Tracker

A Streamlit-based AI assistant that helps patients and caregivers monitor
health status, medications, and wellness habits with intelligent insights.

Built as part of Capabl Internship –  **Medication & Wellness Tracker**.

---

## 🎯 Project Objective

To build a **production-ready health monitoring application** that:

- Tracks medications and adherence
- Monitors daily wellness (steps, sleep, water, mood)
- Analyses vitals and symptoms for risk
- Provides health dashboards, insights, and caregiver summaries
- Supports Indian healthcare context

---

## 🧩 Key Features (Mapped to Track A2 & Week 7–8 Checklist)

### 1. Health Dashboard with Metrics Visualization

- Patient-wise **Health Score (0–100)** combining:
  - Vitals risk
  - Medication adherence
  - Wellness goal completion
- Risk gauge (Low / Moderate / High)
- Smart alerts (e.g., low adherence, low sleep, low activity)
- Vitals snapshot (BP, heart rate, temperature, symptoms)
- Wellness trends (steps, sleep, water) with line charts
- Risk timeline graph (risk over previous visits)

### 2. Medication Tracker & Adherence Monitoring

- Add medication schedule:
  - Patient name, medicine, dosage
  - Frequency (once/twice/thrice a day)
  - Times of day (morning/afternoon/evening/night)
  - Start & end date
- Daily schedule view with **“Mark as taken”** buttons
- Automatic adherence calculation:
  - Per-medication adherence %
  - Overall adherence % per patient
- Adherence bar charts and emoji calendar view
  (✅ taken, ❌ missed, • upcoming, — no medicine)

### 3. Wellness Goals & Progress Analytics

- Set personal goals per patient:
  - **Daily steps goal**
  - **Sleep hours goal**
  - **Water intake goal**
- Log daily wellness:
  - Steps, sleep hours, water intake, mood
- Trend charts for steps, sleep, water
- Streak tracking: consecutive days with logs
- Automatic weekly averages & insights

### 4. AI-Powered Insights & Lifestyle Coaching

- Combines vitals, adherence and wellness data to generate:
  - Risk-based advice
  - Adherence feedback (good / needs attention)
  - Activity, sleep and hydration suggestions
- **AI Lifestyle Coach**:
  - Daily routine guidance
  - Diet suggestions
  - Exercise ideas
  - Sleep & stress tips
  - Medication habit reminders
- **Indian context tips**:
  - Advice tailored to common Indian foods, habits and seasons
  - e.g., salt in pickles/papad, sweets, spicy food, pollution, dengue season

### 5. Family Monitoring & Caregiver Notification

- Generate caregiver summary for multiple family members
- Automatically composes a message including:
  - Recent risk levels
  - Key insights per person
- Caregiver can copy–paste and send via WhatsApp / SMS / email.

### 6. Medical Information Lookup (with sources)

- Search common conditions: hypertension, diabetes, asthma, migraine, depression
- Shows:
  - Overview / definition
  - Common symptoms
  - General self-care tips
  - References (e.g., WHO, CDC, GINA, NIMH etc.)
- For education only – includes medical disclaimer.

### 7. Health Q&A Assistant (Rule-Based)

- Simple Q&A panel:
  - “How many steps should I walk?”
  - “Is my sleep enough?”
  - “How much water should I drink?”
- Uses stored patient data (optional name) to personalise answers.
- Always reminds users to consult a doctor (safety-first).

### 8. Export & Reporting

- Patient health reports:
  - Single patient report (DOCX & PDF)
  - All patient reports (DOCX & PDF)
- Dashboard summary DOCX:
  - Score, vitals, adherence, wellness trends, insights
- Weekly progress PDF:
  - Vitals, adherence, wellness summary, insights
- Data export center:
  - Medication history + log data as CSV
  - Wellness / fitness logs as CSV

### 9. Validation & Error Handling

- Vitals validation:
  - BP format (`120/80`)
  - Numeric checks for heart rate and temperature
- Medication validation:
  - Required fields (patient, name, dosage, time(s) of day)
  - End date cannot be before start date
- Clear error messages using Streamlit (`st.error`) for:
  - Invalid input
  - Database issues
  - Missing required fields

---

## 🏗️ Architecture

- **Frontend:** Streamlit
- **Backend Logic:** Pure Python with modular agent engines:
  - `symptom_extractor`, `disease_engine`, `disease_matcher`
  - `doctor_engine`, `followup_engine`, `treatment_engine`
- **Database:** SQLite (`healthcare.db`)
  - `patients` – vitals, symptoms, risk, diseases
  - `medications` – schedules
  - `medication_logs` – taken doses
  - `wellness_logs` – steps, sleep, water, mood
  - `wellness_goals` – goals per patient
  - `appointments` – doctor appointments (from smart scheduler)
- **Reports:** `python-docx` for DOCX, `reportlab` for PDF

---

## 🛠️ Tech Stack

- Python 3.x  
- Streamlit  
- SQLite3  
- pandas  
- python-docx  
- reportlab  

---

## 📂 Project Structure

```text
healthcare-ai-agent/
│
├── app.py                  # Main Streamlit app
├── healthcare.db           # SQLite database (created at runtime)
├── requirements.txt        # Python dependencies
│
├── agent/
│   ├── symptom_extractor.py
│   ├── disease_engine.py
│   ├── disease_matcher.py
│   ├── doctor_engine.py
│   ├── followup_engine.py
│   ├── treatment_engine.py
│   └── __init__.py
│
├── medical_rules.py        # Vital sign analysis rules
└── README.md               # Project documentation

