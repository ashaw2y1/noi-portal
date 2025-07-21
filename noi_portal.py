import streamlit as st
import pandas as pd
from datetime import date
import os

# Set up page
st.set_page_config(page_title="NOI Portal", layout="centered")
st.title("🧾 NOI Entry Portal")

# CSV file path
file_path = "NOI_log.csv"

# Get the next Credit Note Number
def get_next_credit_note_number():
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        last_number = df.shape[0]
    else:
        last_number = 0
    return f"CN-{last_number + 1:03d}"

# Generate credit note number
credit_note_no = get_next_credit_note_number()

with st.form("credit_note_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Document Serial Number", value=credit_note_no, disabled=True)
    with col2:
        credit_date = st.date_input("Receiving Date", value=date.today())

    col3, col4 = st.columns([1, 2])
    with col3:
        supplier_code = st.text_input("Supplier Code", placeholder="SUP-001")
    with col4:
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

    reason = st.text_area("Comments", height=100)

    uploaded_file = st.file_uploader(
        "📎 Upload Invoice File (PDF or Image)", type=["pdf", "jpg", "jpeg", "png"]
    )

    submitted = st.form_submit_button("✅ Submit")

# Validation and handle submission
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
        errors.append("❌ Please upload the invoice file (PDF or Image).")

    if errors:
        for error in errors:
            st.error(error)
        st.warning("⚠️ Please fill in all required fields before submitting.")
    else:
        # All fields are valid — proceed
        invoice_file_name = "None"
        if uploaded_file:
            ext = os.path.splitext(uploaded_file.name)[1]
            invoice_file_name = f"{credit_note_no}{ext}"

        new_entry = {
            "Serial No": credit_note_no,
            "Date": credit_date.strftime('%Y-%m-%d'),
            "Supplier Code": supplier_code,
            "Supplier Name": supplier_name,
            "Invoice Reference": invoice_ref,
            "Amount": amount,
            "Type": credit_note_type,
            "Comment": reason,
            "Invoice File": invoice_file_name
        }

        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])

        df.to_csv(file_path, index=False)

        # Save uploaded file with serial name
        if uploaded_file:
            upload_dir = "invoices"
            os.makedirs(upload_dir, exist_ok=True)
            with open(os.path.join(upload_dir, invoice_file_name), "wb") as f:
                f.write(uploaded_file.getbuffer())

        st.success(f"✅ Document `{credit_note_no}` submitted successfully!")

# Display previous entries
if os.path.exists(file_path):
    with st.expander("📄 View Submitted Credit Notes"):
        submitted_df = pd.read_csv(file_path)
        st.dataframe(submitted_df.tail(10), use_container_width=True)
