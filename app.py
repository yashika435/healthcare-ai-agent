import sys
sys.path.append(".")
import streamlit as st
import sqlite3
from io import BytesIO
from datetime import datetime
import random

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from agent.symptom_extractor import extract_symptoms
from agent.disease_engine import match_disease, explain_symptoms
from agent.disease_matcher import rank_diseases, DISEASE_KB
from medical_rules import analyze_vitals

from agent.doctor_engine import suggest_specialities, rank_doctors
from agent.followup_engine import estimate_risk_from_symptoms, get_followup_plan
from agent.treatment_engine import get_care_tips


# =====================================================
# SMALL HELPERS
# =====================================================

def disease_name(d):
    """Safely get just the disease name from either a dict or a string."""
    if isinstance(d, dict) and "disease" in d:
        return d["disease"]
    return str(d)


# =====================================================
# DATABASE SETUP
# =====================================================

def init_db():
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            symptoms TEXT,
            bp TEXT,
            heart_rate TEXT,
            temperature TEXT,
            risk_score TEXT,
            possible_diseases TEXT
        )
    """)
    conn.commit()
    conn.close()


def reset_appointment_table():
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS appointments")
    conn.commit()
    conn.close()


reset_appointment_table()


def init_appointments_db():
    """Appointments table (per-doctor schedule)."""
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor TEXT,
            speciality TEXT,
            patient TEXT,
            date TEXT,
            time TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()
init_appointments_db()


def row_to_patient(row):
    keys = [
        "name",
        "age",
        "symptoms",
        "bp",
        "heart_rate",
        "temperature",
        "risk_score",
        "possible_diseases",
    ]
    return dict(zip(keys, row))


def fetch_latest_patient(name: str):
    """Fetch latest patient entry using partial & case-insensitive match."""
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()

    # Case-insensitive + partial match
    name_like = f"%{name.lower()}%"

    c.execute(
        """
        SELECT symptoms, risk_score
        FROM patients
        WHERE LOWER(name) LIKE ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (name_like,),
    )

    result = c.fetchone()
    conn.close()
    return result

# =====================================================
# REPORT GENERATORS (DOCX / PDF)
# =====================================================

def create_docx_for_patient(patient):
    doc = Document()
    doc.add_heading("Healthcare Monitoring Report", level=1)

    doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    doc.add_paragraph("")

    doc.add_paragraph(f"Name: {patient['name']}")
    doc.add_paragraph(f"Age: {patient['age']}")
    doc.add_paragraph(f"Symptoms: {patient['symptoms']}")
    doc.add_paragraph(f"Blood Pressure: {patient['bp']}")
    doc.add_paragraph(f"Heart Rate: {patient['heart_rate']} bpm")
    doc.add_paragraph(f"Temperature: {patient['temperature']} °C")
    doc.add_paragraph(f"Risk Level: {patient['risk_score']}")
    doc.add_paragraph(f"Possible Diseases: {patient['possible_diseases']}")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def create_docx_for_all(patients):
    doc = Document()
    doc.add_heading("All Patient Health Records", level=1)
    doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    doc.add_paragraph("")

    for idx, p in enumerate(patients, start=1):
        doc.add_heading(f"Patient {idx}: {p['name']}", level=2)
        doc.add_paragraph(f"Age: {p['age']}")
        doc.add_paragraph(f"Symptoms: {p['symptoms']}")
        doc.add_paragraph(f"Blood Pressure: {p['bp']}")
        doc.add_paragraph(f"Heart Rate: {p['heart_rate']} bpm")
        doc.add_paragraph(f"Temperature: {p['temperature']} °C")
        doc.add_paragraph(f"Risk Level: {p['risk_score']}")
        doc.add_paragraph(f"Possible Diseases: {p['possible_diseases']}")
        doc.add_paragraph("-" * 40)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def create_pdf_for_patient(patient):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Healthcare Monitoring Report")
    y -= 40

    c.setFont("Helvetica", 11)
    lines = [
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Name: {patient['name']}",
        f"Age: {patient['age']}",
        f"Symptoms: {patient['symptoms']}",
        f"Blood Pressure: {patient['bp']}",
        f"Heart Rate: {patient['heart_rate']} bpm",
        f"Temperature: {patient['temperature']} °C",
        f"Risk Level: {patient['risk_score']}",
        f"Possible Diseases: {patient['possible_diseases']}",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 18

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def create_pdf_for_all(patients):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    for idx, patient in enumerate(patients, start=1):
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Patient {idx}: {patient['name']}")
        y -= 30

        c.setFont("Helvetica", 11)
        lines = [
            f"Age: {patient['age']}",
            f"Symptoms: {patient['symptoms']}",
            f"Blood Pressure: {patient['bp']}",
            f"Heart Rate: {patient['heart_rate']} bpm",
            f"Temperature: {patient['temperature']} °C",
            f"Risk Level: {patient['risk_score']}",
            f"Possible Diseases: {patient['possible_diseases']}",
        ]

        for line in lines:
            c.drawString(50, y, line)
            y -= 18

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


# =====================================================
# MAIN HEADER
# =====================================================

st.markdown(
    "<h1 style='text-align:center; color:#333;'>🩺 Healthcare Monitoring AI Agent</h1>",
    unsafe_allow_html=True,
)
st.write(
    "<p style='text-align:center;'>Analyze symptoms, vitals & get health insights.</p>",
    unsafe_allow_html=True,
)

st.write("Enter your symptoms and vitals to check your health status.")


# =====================================================
# BASIC HEALTH ANALYZER
# =====================================================

name = st.text_input("Full Name")
age = st.number_input("Age", min_value=1, max_value=120)
symptoms = st.text_area("Describe your symptoms")
bp = st.text_input("Blood Pressure (e.g., 120/80)")
heart_rate = st.text_input("Heart Rate (bpm)")
temperature = st.text_input("Body Temperature (°C)")

if st.button("Analyze Health"):
    if name and symptoms and bp and heart_rate and temperature:

        extracted = extract_symptoms(symptoms)
        risk, issues = analyze_vitals(bp, heart_rate, temperature)
        diseases = match_disease(extracted)  # could be list[str] or list[dict]

        st.subheader("🧪 Health Analysis Result")

        if risk == "Low":
            st.success("🟢 Risk Level: LOW")
        elif risk == "Moderate":
            st.warning("🟡 Risk Level: MODERATE")
        else:
            st.error("🔴 Risk Level: HIGH")

        st.write("### Issues detected:")
        for i in issues:
            st.write(f"- {i}")

        st.write("### Possible Diseases:")
        if diseases:
            for d in diseases:
                st.write(f"- {disease_name(d)}")
        else:
            st.write("- Not enough information to guess a condition.")

        # store as comma-separated text of disease names
        possible = ", ".join(disease_name(d) for d in diseases) if diseases else ""

        conn = sqlite3.connect("healthcare.db")
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO patients (
                name, age, symptoms, bp, heart_rate, temperature, risk_score, possible_diseases
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, age, symptoms, bp, heart_rate, temperature, risk, possible),
        )
        conn.commit()
        conn.close()

        st.success("✔ Health data stored and analyzed successfully!")
    else:
        st.error("Please fill all fields.")


# =====================================================
# ADVANCED AI SYMPTOM HELPER
# =====================================================

st.markdown("---")
st.header("🤖 AI Symptom Helper (Advanced Version)")

user_question = st.text_input(
    "Describe your symptoms (e.g., I have fever, cough, body pain):"
)

if st.button("Analyze Symptoms"):
    if not user_question.strip():
        st.error("Please type your symptoms first.")
    else:
        extracted = extract_symptoms(user_question)

        if not extracted:
            st.warning(
                "No known symptoms detected. Try using simple words like 'fever', "
                "'cough', 'headache'."
            )
        else:
            st.success(f"Detected symptoms: {', '.join(extracted)}")

            # Symptom explanations (rule-based)
            explanations = explain_symptoms(extracted)
            if explanations:
                st.subheader("🔍 Symptom Explanations")
                for e in explanations:
                    st.write(f"- {e}")

            # Disease ranking (KB-based)
            ranked = rank_diseases(extracted)
            st.subheader("🩺 Possible Conditions (Ranked)")

            if not ranked:
                st.info("No strong matches found in the disease knowledge base.")
            else:
                top_n = ranked[:3]
                for idx, item in enumerate(top_n, start=1):
                    st.markdown(
                        f"""
**{idx}. {item['disease']}**

- Matched symptoms: {', '.join(item['matched_symptoms'])}  
- Match score: **{item['score']}** / {len(DISEASE_KB[item['disease']])}
                        """
                    )

            # Doctor type recommendation (from doctor_engine)
            st.subheader("👨‍⚕️ Recommended Doctor Type")
            top_disease_name, specialities = suggest_specialities(ranked)
            if top_disease_name:
                st.write(f"Top suspected condition: **{top_disease_name}**")
            if specialities:
                st.write("Suggested specialists:")
                for s in specialities:
                    st.write(f"- {s}")

            # Doctor ranking (external engine)
            st.subheader("🏥 Suggested Doctors")
            ranked_doctors = rank_doctors(specialities)
            for d in ranked_doctors:
                st.write(f"**{d['name']}** — {d['speciality']}")
                st.write(f"Rating: ⭐ {d['rating']} | Exp: {d['experience']} yrs")
                st.markdown("---")
            # Save the top recommended doctor for scheduler
            if ranked_doctors:
                st.session_state.sched_recommended_doctor = ranked_doctors[0]["name"]
                st.session_state.sched_recommended_speciality = ranked_doctors[0]["speciality"]

            # Follow-up plan
            st.subheader("⏰ Follow-up Recommendation")
            symptom_risk = estimate_risk_from_symptoms(extracted)
            f_date, f_msg = get_followup_plan(symptom_risk)
            st.write(f"Risk Level (symptom-based): **{symptom_risk}**")
            st.write(f"Suggested follow-up date: **{f_date}**")
            st.write(f"{f_msg}")

            # Care tips
            st.subheader("💡 Care Suggestions")
            care_tips = get_care_tips(extracted, top_disease_name)
            for tip in care_tips:
                st.write(f"• {tip}")


# =====================================================
# VIEW & EXPORT STORED HEALTH RECORDS
# =====================================================

st.markdown("---")
st.header("📋 View & Export Stored Health Records")

if st.button("Load Patient Records"):
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute(
        """
        SELECT name, age, symptoms, bp, heart_rate, temperature, risk_score, possible_diseases
        FROM patients
        """
    )
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.info("No records found.")
    else:
        st.subheader("Saved Records")
        patients = [row_to_patient(r) for r in rows]

        for p in patients:
            st.write(f"**Name:** {p['name']}")
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {p['symptoms']}")
            st.write(f"**BP:** {p['bp']}")
            st.write(f"**Heart Rate:** {p['heart_rate']}")
            st.write(f"**Temperature:** {p['temperature']}")
            st.write(f"**Risk:** {p['risk_score']}")
            st.write(f"**Possible Diseases:** {p['possible_diseases']}")
            st.markdown("---")

        st.subheader("Export Reports")

        selected_index = st.selectbox(
            "Select a patient to export:",
            options=list(range(len(patients))),
            format_func=lambda i: f"{patients[i]['name']} (Age {patients[i]['age']})",
        )
        selected_patient = patients[selected_index]

        col1, col2 = st.columns(2)

        with col1:
            docx_buf = create_docx_for_patient(selected_patient)
            st.download_button(
                label="⬇ Download selected as DOCX",
                data=docx_buf,
                file_name=f"{selected_patient['name'].replace(' ', '_')}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        with col2:
            pdf_buf = create_pdf_for_patient(selected_patient)
            st.download_button(
                label="⬇ Download selected as PDF",
                data=pdf_buf,
                file_name=f"{selected_patient['name'].replace(' ', '_')}_report.pdf",
                mime="application/pdf",
            )

        st.markdown("### Export All Records")

        all_docx_buf = create_docx_for_all(patients)
        st.download_button(
            label="⬇ Download ALL as DOCX",
            data=all_docx_buf,
            file_name="all_patients_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        all_pdf_buf = create_pdf_for_all(patients)
        st.download_button(
            label="⬇ Download ALL as PDF",
            data=all_pdf_buf,
            file_name="all_patients_report.pdf",
            mime="application/pdf",
        )


# =====================================================
# PATIENT COMMUNICATION TEMPLATES
# =====================================================

st.markdown("---")
st.header("📨 Patient Communication Templates")


def get_latest_patient_for_msg():
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute(
        """
        SELECT name, risk_score, symptoms, possible_diseases
        FROM patients
        ORDER BY id DESC
        LIMIT 1
        """
    )
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "name": row[0],
            "risk": row[1],
            "symptoms": row[2],
            "diseases": row[3],
        }
    return None


def msg_followup(p):
    return f"""
Dear {p['name']},

Based on your recent health evaluation, your overall risk level was **{p['risk']}**.

Recorded symptoms:
{p['symptoms']}

Possible conditions:
{p['diseases']}

👉 Please monitor your symptoms for any changes.  
👉 Stay hydrated, take enough rest, and follow your medication schedule.  
👉 If your symptoms worsen or new symptoms appear, seek medical care immediately.

Wishing you good health,  
Healthcare Monitoring AI Agent
"""


def msg_emergency(p):
    return f"""
Dear {p['name']},

Our recent assessment shows your risk level as **{p['risk']}**.

Symptoms noted:
{p['symptoms']}

Possible serious conditions:
{p['diseases']}

⚠ We recommend that you **do not ignore these symptoms**.

• If you experience chest pain, severe breathlessness, confusion, or fainting,  
  please visit the nearest emergency department immediately.  

Stay safe,  
Healthcare Monitoring AI Agent
"""


def msg_recovery_reminder(p):
    return f"""
Hello {p['name']},

This is a gentle reminder to support your recovery.

Your last check showed risk level: **{p['risk']}**  
Symptoms: {p['symptoms']}

Please remember:
• Take prescribed medicines on time.  
• Do not skip doses without asking your doctor.  
• Get enough rest and sleep.  

Get well soon!  
Healthcare Monitoring AI Agent
"""


def msg_lifestyle_diet(p):
    return f"""
Hi {p['name']},

Here are some lifestyle and diet suggestions based on your recent checkup.

Symptoms: {p['symptoms']}  
Possible conditions: {p['diseases']}

General tips:
• Drink 2–3 litres of water a day (unless your doctor advised restriction).  
• Include fruits, vegetables, and whole grains in your meals.  
• Avoid very oily, spicy, or junk food.  
• Limit sugary drinks and smoking/alcohol (if applicable).  

These are general suggestions and do not replace a doctor's advice.

With care,  
Healthcare Monitoring AI Agent
"""


def msg_appointment_confirmation(p, when_text):
    return f"""
Dear {p['name']},

Your medical appointment has been booked.

🗓 Appointment details:
• Patient: {p['name']}  
• Date & Time: {when_text}

Recent assessment:
• Risk level: {p['risk']}  
• Symptoms: {p['symptoms']}  
• Possible conditions: {p['diseases']}

Please reach the clinic/hospital 10–15 minutes early and
carry your previous medical reports and medicine list.

Regards,  
Healthcare Monitoring AI Agent
"""


template_type = st.selectbox(
    "Choose a template to generate:",
    [
        "Follow-up Advice",
        "Emergency Alert",
        "Recovery / Medicine Reminder",
        "Lifestyle & Diet Suggestions",
        "Appointment Confirmation",
    ],
)

appt_datetime_text = None
if template_type == "Appointment Confirmation":
    c1, c2 = st.columns(2)
    with c1:
        appt_date_msg = st.date_input("Select appointment date")
    with c2:
        appt_time_msg = st.time_input("Select appointment time")
    appt_datetime_text = (
        f"{appt_date_msg.strftime('%Y-%m-%d')} at {appt_time_msg.strftime('%H:%M')}"
    )

if st.button("Generate Message"):
    p = get_latest_patient_for_msg()
    if not p:
        st.warning("⚠ No patient data found. Please analyze at least one patient first.")
    else:
        if template_type == "Follow-up Advice":
            message = msg_followup(p)
        elif template_type == "Emergency Alert":
            message = msg_emergency(p)
        elif template_type == "Recovery / Medicine Reminder":
            message = msg_recovery_reminder(p)
        elif template_type == "Lifestyle & Diet Suggestions":
            message = msg_lifestyle_diet(p)
        else:
            message = msg_appointment_confirmation(p, appt_datetime_text)

        st.subheader("Generated Message")
        st.text_area("You can copy this message:", message, height=260)


# =====================================================
# DOCTOR SPECIALITY MAPPING FOR SCHEDULER (fallback)
# =====================================================

def scheduler_speciality(disease):
    mapping = {
        "Hypertension": "Cardiologist",
        "Hypertension (High BP)": "Cardiologist",
        "Diabetes": "Endocrinologist",
        "Asthma": "Pulmonologist",
        "Migraine": "Neurologist",
        "Flu": "General Physician",
        "COVID-19": "Pulmonologist",
        "Gastritis": "Gastroenterologist",
        "UTI": "Urologist",
        "Arthritis": "Rheumatologist",
        "Skin Allergy": "Dermatologist",
        "Depression": "Psychiatrist",
        "Anxiety": "Psychiatrist",
        "Thyroid Disorder": "Endocrinologist",
        "Dengue": "General Physician",
        "Viral Fever": "General Physician",
        "Heart Disease": "Cardiologist",
        "Kidney Stone": "Urologist",
        "PCOS": "Gynecologist",
        "Pregnancy": "Gynecologist",
        "Ear Infection": "ENT Specialist",
        "Common Cold": "General Physician",
        "Acidity": "Gastroenterologist",
    }
    return mapping.get(disease, "General Physician")


# 19-speciality doctor DB (for scheduler)
DOCTOR_DB = {
    "General Physician": [
        {"name": "Dr. Anil Kumar", "experience": 12},
        {"name": "Dr. Swetha Rao", "experience": 8},
        {"name": "Dr. Rajesh Singh", "experience": 15},
    ],
    "Cardiologist": [
        {"name": "Dr. Meera Nair", "experience": 14},
        {"name": "Dr. Ashok Patil", "experience": 10},
        {"name": "Dr. Virat Shah", "experience": 18},
    ],
    "Neurologist": [
        {"name": "Dr. Sahana Iyer", "experience": 9},
        {"name": "Dr. Rishi Menon", "experience": 13},
        {"name": "Dr. Neha Bhat", "experience": 11},
    ],
    "Dermatologist": [
        {"name": "Dr. Kavya Shetty", "experience": 7},
        {"name": "Dr. Rohan Kapoor", "experience": 12},
        {"name": "Dr. Trisha Jain", "experience": 10},
    ],
    "ENT Specialist": [
        {"name": "Dr. Jayanth Kulkarni", "experience": 10},
        {"name": "Dr. Pooja Sharma", "experience": 6},
        {"name": "Dr. Raghav Mehta", "experience": 9},
    ],
    "Orthopedic": [
        {"name": "Dr. Manoj Reddy", "experience": 16},
        {"name": "Dr. Divya Joshi", "experience": 11},
        {"name": "Dr. Jay Patel", "experience": 14},
    ],
    "Gastroenterologist": [
        {"name": "Dr. Nikita Das", "experience": 10},
        {"name": "Dr. Karthik S", "experience": 12},
        {"name": "Dr. Mahesh Agarwal", "experience": 15},
    ],
    "Psychiatrist": [
        {"name": "Dr. Ananya Rao", "experience": 8},
        {"name": "Dr. Varun Khanna", "experience": 10},
        {"name": "Dr. Radhika Pillai", "experience": 11},
    ],
    "Pulmonologist": [
        {"name": "Dr. Harish Prasad", "experience": 13},
        {"name": "Dr. Sneha M", "experience": 9},
        {"name": "Dr. Ajay Verma", "experience": 7},
    ],
    "Endocrinologist": [
        {"name": "Dr. Sonia Mishra", "experience": 12},
        {"name": "Dr. Farhan Khan", "experience": 15},
        {"name": "Dr. Ritu Malhotra", "experience": 9},
    ],
    "Diabetologist": [
        {"name": "Dr. Sunil Shetty", "experience": 10},
        {"name": "Dr. Priya Desai", "experience": 11},
        {"name": "Dr. Mohan Rao", "experience": 7},
    ],
    "Nephrologist": [
        {"name": "Dr. Kavita R", "experience": 14},
        {"name": "Dr. Naveen P", "experience": 10},
        {"name": "Dr. Aarav Kumar", "experience": 8},
    ],
    "Urologist": [
        {"name": "Dr. Prasad Gowda", "experience": 13},
        {"name": "Dr. Divya Patel", "experience": 7},
        {"name": "Dr. Jayant S", "experience": 11},
    ],
    "Gynecologist": [
        {"name": "Dr. Aishwarya N", "experience": 12},
        {"name": "Dr. Farida Khan", "experience": 15},
        {"name": "Dr. Manasa M", "experience": 9},
    ],
    "Pediatrician": [
        {"name": "Dr. Nandini R", "experience": 10},
        {"name": "Dr. Aditya S", "experience": 8},
        {"name": "Dr. Mehul Jain", "experience": 13},
    ],
    "Oncologist": [
        {"name": "Dr. Ramesh N", "experience": 16},
        {"name": "Dr. Shruti Arora", "experience": 12},
        {"name": "Dr. Vivek Rao", "experience": 14},
    ],
    "Rheumatologist": [
        {"name": "Dr. Sanjana Rao", "experience": 11},
        {"name": "Dr. Ajith K", "experience": 9},
        {"name": "Dr. Preeti Narang", "experience": 12},
    ],
    "Hematologist": [
        {"name": "Dr. Anoop S", "experience": 13},
        {"name": "Dr. Megha R", "experience": 7},
        {"name": "Dr. Suraj R", "experience": 10},
    ],
    "Ophthalmologist": [
        {"name": "Dr. Kiran Shetty", "experience": 15},
        {"name": "Dr. Nisha Kapoor", "experience": 11},
        {"name": "Dr. Rohit Bhat", "experience": 9},
    ],
}

# random availability table
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS = ["10:00 AM", "1:00 PM", "4:00 PM"]

# Make all doctors available on ALL days with same 3 slots
DOCTOR_AVAILABILITY = {}
for speciality, doctors in DOCTOR_DB.items():
    DOCTOR_AVAILABILITY[speciality] = {}
    for d in doctors:
        name_doc = d["name"]
        DOCTOR_AVAILABILITY[speciality][name_doc] = {
            day: SLOTS[:] for day in DAYS  # all 6 days
        }



def weekday_from_date(dt):
    return dt.strftime("%a")  # Mon/Tue/...


# =====================================================
# SMART APPOINTMENT SCHEDULER (SINGLE, CLEAN VERSION)
# =====================================================

st.markdown("---")
st.header("📅 Smart Appointment Scheduler (AI Recommended)")

appt_patient_name = st.text_input("Patient Name for Appointment:")

# State for scheduler
if "sched_speciality" not in st.session_state:
    st.session_state.sched_speciality = None
if "sched_disease" not in st.session_state:
    st.session_state.sched_disease = None
if "sched_doctor" not in st.session_state:
    st.session_state.sched_doctor = None
if "sched_date" not in st.session_state:
    st.session_state.sched_date = None
if "sched_recommended_doctor" not in st.session_state:
    st.session_state.sched_recommended_doctor = None

# STEP 1 – infer disease & speciality from last analysis
if st.button("Find Recommended Doctor"):
    if not appt_patient_name.strip():
        st.error("Please enter patient name.")
    else:
        latest = fetch_latest_patient(appt_patient_name)
        if latest is None:
            st.warning("⚠ No previous health analysis found for this patient.")
        else:
            stored_symptoms, stored_risk = latest
            extracted = extract_symptoms(stored_symptoms)
            ranked = rank_diseases(extracted)

            if not ranked:
                st.warning("Cannot detect disease. Try adding more symptoms.")
            else:

                # 🚀 Use ONLY the doctor_engine mapping
                top_disease_name, specialities = suggest_specialities(ranked)

                # 🚀 Choose the FIRST speciality as the recommended specialist
                final_speciality = specialities[0]

                # Save result
                st.session_state.sched_speciality = final_speciality
                st.session_state.sched_disease = top_disease_name

                st.success(f"Detected Condition: **{top_disease_name}**")
                st.info(f"Recommended Specialist: **{final_speciality}**")
# STEP 2 – doctor selection (fixed to the recommended doctor)
if st.session_state.sched_speciality:

    recommended_doc = st.session_state.get("sched_recommended_doctor")
    recommended_spec = st.session_state.get("sched_recommended_speciality")

    if recommended_doc:
        st.subheader("👨‍⚕️ Assigned Doctor")
        st.success(f"{recommended_doc} — {recommended_spec}")

        # Lock doctor selection
        st.session_state.sched_doctor = recommended_doc
    else:
        st.warning("No recommended doctor found. Please run AI Symptom Helper first.")
# STEP 3 – date + slots
if st.session_state.sched_doctor:
    st.subheader("📆 Select Appointment Date")
    appt_date = st.date_input("Choose a date")
    st.session_state.sched_date = appt_date

    if appt_date:
        weekday = weekday_from_date(appt_date)
        doctor = st.session_state.sched_doctor

        st.write(f"Selected Day: **{weekday}**")

        slots_map = DOCTOR_AVAILABILITY[
            st.session_state.sched_speciality
        ].get(doctor, {})

        if weekday in slots_map:
            slots = slots_map[weekday]
            st.subheader("🕒 Available Slots")
            selected_slot = st.radio("Choose a time slot:", slots)

            # STEP 4 – confirm + store in DB
            if st.button("Confirm Appointment"):
                conn = sqlite3.connect("healthcare.db")
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO appointments (doctor, speciality, patient, date, time)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        doctor,
                        st.session_state.sched_speciality,
                        appt_patient_name,
                        appt_date.strftime("%Y-%m-%d"),
                        selected_slot,
                    ),
                )
                conn.commit()
                conn.close()

                st.success(
                    f"✔ Appointment Confirmed!\n\n"
                    f"📌 Patient: **{appt_patient_name}**\n"
                    f"👨‍⚕️ Doctor: **{doctor}**\n"
                    f"🏥 Speciality: **{st.session_state.sched_speciality}**\n"
                    f"📅 Date: **{appt_date.strftime('%Y-%m-%d')}**\n"
                    f"⏰ Time: **{selected_slot}**"
                )
        else:
            st.warning("❌ This doctor is not available on the selected day.")
