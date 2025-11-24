from datetime import datetime, timedelta
import sqlite3

# Generates next 7 days
def get_next_7_days():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

# Fixed time slots for all doctors
TIME_SLOTS = [
    "10:00 AM", "10:30 AM", "11:00 AM",
    "5:00 PM", "5:30 PM", "6:00 PM"
]

# Check if slot is booked
def is_slot_booked(doctor, date, time):
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("""SELECT * FROM appointments 
                 WHERE doctor=? AND date=? AND time=?""",
              (doctor, date, time))
    result = c.fetchone()
    conn.close()
    return result is not None

# Returns all available slots for a doctor
def get_available_slots(doctor):
    calendar = {}
    days = get_next_7_days()

    for d in days:
        calendar[d] = []
        for t in TIME_SLOTS:
            if is_slot_booked(doctor, d, t):
                calendar[d].append({"time": t, "status": "booked"})
            else:
                calendar[d].append({"time": t, "status": "free"})

    return calendar

# Book a slot
def book_slot(doctor, speciality, patient, date, time):
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO appointments (doctor, speciality, patient, date, time)
        VALUES (?, ?, ?, ?, ?)
    """, (doctor, speciality, patient, date, time))
    conn.commit()
    conn.close()
    return True
