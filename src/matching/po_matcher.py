import pandas as pd


def load_purchase_orders(
    csv_path: str = "data/po/purchase_orders.csv",
) -> pd.DataFrame:
    """Load approved purchase orders from the PO dataset."""
    return pd.read_csv(csv_path)


def find_purchase_order(
    po_number: str,
    csv_path: str = "data/po/purchase_orders.csv",
):
    """Find a purchase order by PO number.

    Returns None when the invoice does not contain a PO number
    or when no matching PO exists.
    """

    # Missing PO number should not crash the pipeline.
    if not po_number:
        return None

    purchase_orders = load_purchase_orders(csv_path)

    matches = purchase_orders[
        purchase_orders["po_number"].astype(str).str.upper()
        == po_number.upper()
    ]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict() 