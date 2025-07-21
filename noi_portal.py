import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, date

# --------------- CONFIG ---------------
st.set_page_config(page_title="NOI Portal", layout="centered")

# --------------- DATABASE CONNECTION ---------------

def get_connection():
    return psycopg2.connect(st.secrets["database"]["url"])

# --------------- USER AUTHENTICATION ---------------
st.sidebar.header("🔐 Login")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    # Example user credentials (Replace with database check later)
    valid_users = {
        "user1@example.com": "pass123",
        "admin@sg.com": "admin456"
    }

    if login_button:
        if email in valid_users and password == valid_users[email]:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# --------------- FORM ----------------
st.title("🧾 NOI Entry Portal")

with st.form("credit_note_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        credit_date = st.date_input("Receiving Date", value=date.today())
    with col2:
        supplier_code = st.text_input("Supplier Code", placeholder="SUP-001")

    supplier_name = st.text_input("Supplier Name")
    invoice_ref = st.text_input("Invoice Reference")
    amount = st.number_input("Value", min_value=0.0, format="%.2f")

    credit_note_type = st.selectbox(
        "Type",
        [
            "Donation",
            "Enlisting Fees / Access Card Fee",
            "Credit Notes",
            "Scientific Support",
            "RTF Deal"
        ]
    )

    comment = st.text_area("Comments (optional)", height=100)
    uploaded_file = st.file_uploader(
        "📎 Upload Invoice File (PDF or Image)", type=["pdf", "jpg", "jpeg", "png"]
    )

    submitted = st.form_submit_button("✅ Submit")

# --------------- HANDLE SUBMISSION ---------------
if submitted:
    errors = []

    if not supplier_code.strip():
        errors.append("❌ Supplier Code is required.")
    if not supplier_name.strip():
        errors.append("❌ Supplier Name is required.")
    if not invoice_ref.strip():
        errors.append("❌ Invoice Reference is required.")
    if amount <= 0:
        errors.append("❌ Value must be greater than 0.")
    if not uploaded_file:
        errors.append("❌ Please upload the invoice file.")

    if errors:
        for error in errors:
            st.error(error)
        st.warning("⚠️ Please fix the above errors.")
    else:
        # Generate filename for upload
        ext = os.path.splitext(uploaded_file.name)[1]
        invoice_file_name = f"temp{ext}"  # temp, will rename after insert

        # Connect and insert into Supabase PostgreSQL
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO noi_entries (
                    submitted_by, submitted_at, date,
                    supplier_code, supplier_name, invoice_ref,
                    amount, type, comment, invoice_file_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                st.session_state.user_email,
                datetime.now(),
                credit_date,
                supplier_code,
                supplier_name,
                invoice_ref,
                amount,
                credit_note_type,
                comment,
                invoice_file_name
            ))

            record_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            # Save file with proper name
            final_filename = f"NOI-{record_id}{ext}"
            upload_dir = "invoices"
            os.makedirs(upload_dir, exist_ok=True)
            with open(os.path.join(upload_dir, final_filename), "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ Submission successful! Document ID: {record_id}")
            st.info(f"📎 File saved as: `{final_filename}`")

        except Exception as e:
            st.error(f"❌ Failed to submit: {e}")
