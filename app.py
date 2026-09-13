import os
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="InvoiceIQ",
    page_icon="🧾",
    layout="wide",
)

st.title("🧾 InvoiceIQ")
st.subheader("AI-Powered Invoice Processing & Decision Engine")
st.write(
    "Upload an invoice PDF to extract invoice data, match it against "
    "purchase-order information, validate business rules, detect duplicates, "
    "and produce an explainable decision."
)

st.divider()

with st.sidebar:
    st.header("Processing Flow")
    st.write("1. 📄 Invoice Upload")
    st.write("2. 🔍 Data Extraction")
    st.write("3. 📋 PO Matching")
    st.write("4. ✅ Validation")
    st.write("5. 🔁 Duplicate Check")
    st.write("6. ⚖️ Decision Engine")
    st.write("7. 📝 Explanation")

st.header("📄 Upload Invoice")

uploaded_file = st.file_uploader(
    "Upload an invoice PDF",
    type=["pdf"],
)

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("🚀 Process Invoice", type="primary"):

        os.makedirs("data/invoices", exist_ok=True)

        file_path = os.path.join(
            "data/invoices",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.header("⚙️ Processing")

        progress = st.progress(0)

        stages = [
            ("📄 Reading invoice document", 15),
            ("🔍 Extracting invoice information", 30),
            ("📋 Matching purchase order", 50),
            ("✅ Validating business rules", 70),
            ("🔁 Checking duplicate invoice", 85),
        ]

        for message, value in stages:
            st.write(message)
            progress.progress(value)

        try:
            from src.pipeline import process_invoice

            result = process_invoice(file_path)

            progress.progress(100)
            st.success("Invoice processing completed.")

        except Exception as e:
            st.error("Invoice processing failed.")
            st.exception(e)
            st.stop()

        st.divider()
        st.header("⚖️ Final Decision")

        decision = result.get("decision", "UNKNOWN")

        if decision == "APPROVED":
            st.success("✅ APPROVED")
        elif decision == "PENDING REVIEW":
            st.warning("⚠️ PENDING REVIEW")
        elif decision == "REJECTED":
            st.error("❌ REJECTED")
        else:
            st.info(f"Decision: {decision}")

        reasons = result.get("reasons", [])

        if reasons:
            st.subheader("📝 Decision Explanation")
            for reason in reasons:
                st.write(f"• {reason}")

        st.divider()
        st.header("📊 Processing Details")

        invoice = result.get("invoice")

        if invoice:
            st.subheader("Extracted Invoice Data")
            st.json(invoice)

        po = result.get("po")

        if po:
            st.subheader("Purchase Order Match")
            st.json(po)
        else:
            st.warning("No matching purchase order found.")

        validation = result.get("validation")

        if validation:
            st.subheader("Validation Results")

            if hasattr(validation, "model_dump"):
                validation = validation.model_dump()
            elif hasattr(validation, "dict"):
                validation = validation.dict()

            st.json(validation)

        duplicate = result.get("duplicate")

        st.subheader("Duplicate Check")

        if duplicate:
            st.error("❌ Duplicate invoice detected")
        else:
            st.success("✓ No duplicate invoice detected")

        st.divider()
        st.header("🔎 Complete Pipeline Result")
        st.json(result)

        st.divider()
        st.header("📊 Run Summary")

        st.write(
            f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Decision:** {decision}")

else:
    st.info("Upload an invoice PDF to begin processing.")

st.divider()

st.header("📌 InvoiceIQ MVP")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Workflow", "End-to-End")

with col2:
    st.metric("Decision Types", "3")

with col3:
    st.metric("Edge Cases", "4")

st.caption(
    "InvoiceIQ automates invoice extraction, PO matching, validation, "
    "duplicate detection, and explainable decisioning."
)
