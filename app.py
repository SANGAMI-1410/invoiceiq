import os
from datetime import datetime

import streamlit as st

from src.pipeline import process_invoice
from src.extraction.invoice_extractor import extract_invoice
from src.matching.po_matcher import find_purchase_order
from src.validation.validator import validate_invoice_against_po


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="InvoiceIQ",
    page_icon="🧾",
    layout="wide",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "run_history" not in st.session_state:
    st.session_state.run_history = []


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def get_decision_message(decision):
    if decision == "APPROVED":
        return "Invoice passed all required checks."
    elif decision == "PENDING REVIEW":
        return "Invoice requires manual review."
    elif decision == "REJECTED":
        return "Invoice failed one or more business rules."
    return "Invoice processing completed."


def save_uploaded_file(uploaded_file):
    """
    Save uploaded invoice into the project's invoice folder.
    """
    invoice_folder = "data/invoices"
    os.makedirs(invoice_folder, exist_ok=True)

    file_path = os.path.join(
        invoice_folder,
        uploaded_file.name
    )

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path


def build_detailed_result(file_path):
    """
    Run the existing backend pipeline and additionally collect
    invoice, PO, validation, and duplicate information for the UI.
    """

    # Run the actual production pipeline
    result = process_invoice(file_path)

    # Extract invoice data separately for UI visibility
    invoice_object = extract_invoice(file_path)

    # Convert Pydantic model to dictionary
    if hasattr(invoice_object, "model_dump"):
        invoice = invoice_object.model_dump()
    else:
        invoice = invoice_object.dict()

    # Find PO
    po = None

    if invoice.get("po_number"):
        po = find_purchase_order(
            invoice["po_number"]
        )

    # Validation
    validation = None

    if po:
        validation = validate_invoice_against_po(
            invoice_object,
            po
        )

    # Determine duplicate state from the final result
    decision = result.get(
        "decision",
        "UNKNOWN"
    )

    reasons = result.get(
        "reasons",
        []
    )

    duplicate = (
        decision == "REJECTED"
        and any(
            "duplicate" in str(reason).lower()
            for reason in reasons
        )
    )

    return {
        "invoice": invoice,
        "po": po,
        "validation": validation,
        "duplicate": duplicate,
        "decision": decision,
        "reasons": reasons,
    }


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🧾 InvoiceIQ")

st.subheader(
    "AI-Powered Invoice Processing & Decision Engine"
)

st.write(
    "Upload an invoice PDF and InvoiceIQ will extract "
    "invoice data, validate it against purchase-order "
    "rules, detect duplicates, and produce an "
    "explainable decision."
)

st.divider()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("InvoiceIQ")

    st.write("### Processing Flow")

    st.write("1. 📄 Invoice Upload")
    st.write("2. 🔍 Data Extraction")
    st.write("3. 📋 PO Matching")
    st.write("4. ✅ Validation")
    st.write("5. 🔁 Duplicate Check")
    st.write("6. ⚖️ Decision Engine")
    st.write("7. 📝 Explanation")

    st.divider()

    st.caption("InvoiceIQ MVP")
    st.caption("Finance / Accounts Payable Automation")


# ---------------------------------------------------------
# Upload section
# ---------------------------------------------------------

st.header("1. Upload Invoice")

uploaded_file = st.file_uploader(
    "Upload an invoice PDF",
    type=["pdf"],
    help=(
        "Upload a machine-readable or scanned "
        "invoice PDF."
    ),
)


if uploaded_file is not None:

    st.success(
        f"Invoice uploaded: {uploaded_file.name}"
    )

    st.divider()

    # -----------------------------------------------------
    # Run processing
    # -----------------------------------------------------

    if st.button(
        "🚀 Process Invoice",
        type="primary"
    ):

        file_path = save_uploaded_file(
            uploaded_file
        )

        st.header("2. Processing Invoice")

        # -------------------------------------------------
        # Stage display
        # -------------------------------------------------

        stage_container = st.container()

        with stage_container:

            st.write(
                "📄 **Stage 1 — Reading invoice document**"
            )

            progress = st.progress(10)

            st.write(
                "🔍 **Stage 2 — Extracting invoice information**"
            )

            progress.progress(25)

            st.write(
                "📋 **Stage 3 — Matching purchase order**"
            )

            progress.progress(45)

            st.write(
                "✅ **Stage 4 — Validating business rules**"
            )

            progress.progress(65)

            st.write(
                "🔁 **Stage 5 — Checking duplicate invoice**"
            )

            progress.progress(80)

            # -------------------------------------------------
            # Run backend
            # -------------------------------------------------

            try:

                result = build_detailed_result(
                    file_path
                )

                progress.progress(100)

                st.success(
                    "Invoice processing completed successfully."
                )

            except Exception as error:

                progress.empty()

                st.error(
                    "Invoice processing failed."
                )

                st.exception(error)

                st.stop()


        # -----------------------------------------------------
        # Extract results
        # -----------------------------------------------------

        invoice = result.get(
            "invoice",
            {}
        )

        po = result.get(
            "po"
        )

        validation = result.get(
            "validation"
        )

        duplicate = result.get(
            "duplicate",
            False
        )

        decision = result.get(
            "decision",
            "UNKNOWN"
        )

        reasons = result.get(
            "reasons",
            []
        )


        # -----------------------------------------------------
        # Final decision
        # -----------------------------------------------------

        st.divider()

        st.header("3. Final Decision")

        if decision == "APPROVED":

            st.success(
                f"### ✅ {decision}"
            )

        elif decision == "PENDING REVIEW":

            st.warning(
                f"### ⚠️ {decision}"
            )

        elif decision == "REJECTED":

            st.error(
                f"### ❌ {decision}"
            )

        else:

            st.info(
                f"### {decision}"
            )


        st.write(
            get_decision_message(decision)
        )


        # -----------------------------------------------------
        # Extracted invoice information
        # -----------------------------------------------------

        st.divider()

        st.header(
            "4. Extracted Invoice Data"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Vendor",
                invoice.get(
                    "vendor",
                    "N/A"
                )
            )

            st.metric(
                "Invoice Number",
                invoice.get(
                    "invoice_number",
                    "N/A"
                )
            )

        with col2:

            st.metric(
                "PO Number",
                invoice.get(
                    "po_number"
                ) or "Missing"
            )

            st.metric(
                "Currency",
                invoice.get(
                    "currency",
                    "N/A"
                )
            )

        with col3:

            total = invoice.get(
                "total",
                0
            )

            tax = invoice.get(
                "tax",
                0
            ) or 0

            st.metric(
                "Invoice Total",
                f"{float(total):,.2f}"
            )

            st.metric(
                "Tax",
                f"{float(tax):,.2f}"
            )


        # -----------------------------------------------------
        # Purchase order information
        # -----------------------------------------------------

        st.divider()

        st.header(
            "5. Purchase Order Match"
        )

        if po:

            po_col1, po_col2, po_col3 = (
                st.columns(3)
            )

            with po_col1:

                st.write(
                    "**PO Number**"
                )

                st.write(
                    po.get(
                        "po_number",
                        "N/A"
                    )
                )

            with po_col2:

                st.write(
                    "**PO Vendor**"
                )

                st.write(
                    po.get(
                        "vendor",
                        "N/A"
                    )
                )

            with po_col3:

                st.write(
                    "**PO Total**"
                )

                st.write(
                    f"{float(po.get('total_amount', 0)):,.2f}"
                )

        else:

            st.warning(
                "No matching purchase order was found."
            )


        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        st.divider()

        st.header(
            "6. Validation Results"
        )

        if validation:

            checks = validation.get(
                "checks",
                {}
            )

            val_col1, val_col2 = (
                st.columns(2)
            )

            with val_col1:

                st.write(
                    "### Purchase Order"
                )

                if po:

                    st.success(
                        "✓ PO found"
                    )

                else:

                    st.error(
                        "✗ PO not found"
                    )

                st.write(
                    "### Vendor"
                )

                if checks.get(
                    "vendor_match"
                ):

                    st.success(
                        "✓ Vendor matches PO"
                    )

                else:

                    st.error(
                        "✗ Vendor mismatch"
                    )

            with val_col2:

                st.write(
                    "### Currency"
                )

                if checks.get(
                    "currency_match"
                ):

                    st.success(
                        "✓ Currency matches"
                    )

                else:

                    st.error(
                        "✗ Currency mismatch"
                    )

                st.write(
                    "### Amount Tolerance"
                )

                if checks.get(
                    "amount_within_tolerance"
                ):

                    st.success(
                        "✓ Amount within tolerance"
                    )

                else:

                    st.error(
                        "✗ Amount exceeds tolerance"
                    )


            amount_difference = checks.get(
                "amount_difference",
                0
            )

            tolerance_amount = checks.get(
                "tolerance_amount",
                0
            )

            st.write(
                f"**Amount difference:** "
                f"{float(amount_difference):,.2f}"
            )

            st.write(
                f"**Allowed tolerance:** "
                f"{float(tolerance_amount):,.2f}"
            )

        else:

            st.info(
                "Validation could not be performed "
                "because no matching PO was found."
            )


        # -----------------------------------------------------
        # Duplicate detection
        # -----------------------------------------------------

        st.divider()

        st.header(
            "7. Duplicate Check" 
        )

        if duplicate:

            st.error(
                "❌ Duplicate invoice detected"
            )

        else:

            st.success(
                "✓ No duplicate invoice detected"
            )


        # -----------------------------------------------------
        # Decision explanation
        # -----------------------------------------------------

        st.divider()

        st.header(
            "8. Decision Explanation"
        )

        if reasons:

            for reason in reasons:

                st.write(
                    f"• {reason}"
                )

        else:

            st.write(
                "No additional issues were identified."
            )


        # -----------------------------------------------------
        # Run history
        # -----------------------------------------------------

        st.session_state.run_history.insert(
            0,
            {
                "time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "invoice": invoice.get(
                    "invoice_number",
                    "N/A"
                ),
                "vendor": invoice.get(
                    "vendor",
                    "N/A"
                ),
                "total": float(
                    invoice.get(
                        "total",
                        0
                    )
                ),
                "decision": decision,
            }
        )


# ---------------------------------------------------------
# Processing history dashboard
# ---------------------------------------------------------

st.divider()

st.header(
    "📊 Processing History"
)

if st.session_state.run_history:

    for run in st.session_state.run_history:

        with st.expander(
            f"{run['invoice']} — "
            f"{run['decision']}"
        ):

            history_col1, history_col2 = (
                st.columns(2)
            )

            with history_col1:

                st.write(
                    f"**Vendor:** "
                    f"{run['vendor']}"
                )

                st.write(
                    f"**Invoice Total:** "
                    f"{run['total']:,.2f}"
                )

            with history_col2:

                st.write(
                    f"**Processed:** "
                    f"{run['time']}"
                )

                st.write(
                    f"**Decision:** "
                    f"{run['decision']}"
                ) 

else:

    st.info(
        "No invoices have been processed "
        "during this session yet."
    ) 