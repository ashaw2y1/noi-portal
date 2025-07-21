import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# --------------- CONFIG ---------------
st.set_page_config(page_title="NOI Portal", layout="centered")

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
        # Save file locally
        ext = os.path.splitext(uploaded_file.name)[1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        final_filename = f"NOI-{timestamp}{ext}"

        upload_dir = "invoices"
        os.makedirs(upload_dir, exist_ok=True)
        with open(os.path.join(upload_dir, final_filename), "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save entry to a CSV log
        df_row = pd.DataFrame([{
            "Date": credit_date,
            "Supplier Code": supplier_code,
            "Supplier Name": supplier_name,
            "Invoice Ref": invoice_ref,
            "Amount": amount,
            "Type": credit_note_type,
            "Comment": comment,
            "Filename": final_filename,
            "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        csv_path = "noi_records.csv"
        if os.path.exists(csv_path):
            df_existing = pd.read_csv(csv_path)
            df_final = pd.concat([df_existing, df_row], ignore_index=True)
        else:
            df_final = df_row

        df_final.to_csv(csv_path, index=False)

        st.success(f"✅ Submission successful!")
        st.info(f"📎 File saved as: `{final_filename}`")
