import sqlite3


def initialize_database(db_path: str = "data/invoiceiq.db"):
    """Create the invoice history table if it does not exist."""

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            invoice_number TEXT NOT NULL,
            invoice_date TEXT,
            total REAL,
            decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vendor, invoice_number)
        )
        """
    )

    connection.commit()
    connection.close()


def is_duplicate_invoice(
    vendor: str,
    invoice_number: str,
    db_path: str = "data/invoiceiq.db",
) -> bool:
    """Check whether this invoice has already been processed."""

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM processed_invoices
        WHERE LOWER(vendor) = LOWER(?)
        AND LOWER(invoice_number) = LOWER(?)
        LIMIT 1
        """,
        (vendor, invoice_number),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def save_processed_invoice(
    vendor: str,
    invoice_number: str,
    invoice_date: str,
    total: float,
    decision: str,
    db_path: str = "data/invoiceiq.db",
):
    """Save a processed invoice to the database."""

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO processed_invoices
        (vendor, invoice_number, invoice_date, total, decision)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            vendor,
            invoice_number,
            invoice_date,
            total,
            decision,
        ),
    )

    connection.commit()
    connection.close() 