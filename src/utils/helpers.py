import fitz
import re
import pandas as pd

from src.settings import settings


# ---------------------------------
# Extract note from UPI transaction
# ---------------------------------

def extract_note(particulars):

    match = re.search(
        r'UPI/[^/]+/[^/]+/([^/]+)/',
        particulars,
        re.IGNORECASE
    )

    if not match:
        return None

    note = match.group(1).strip()

    ignore_values = {
        "",
        "UPI",
        "PAY",
        "PAYMENT",
        "UPI PAYMENT"
    }

    if note.upper() in ignore_values:
        return None

    return note


# ---------------------------------
# Extract merchant
# ---------------------------------

def extract_merchant(particulars):

    if "/" in particulars:
        return particulars.split("/")[0].strip()

    return particulars.strip()


# ---------------------------------
# Process PDF
# ---------------------------------

def process_pdf(pdf_bytes):

    # ---------------------------------
    # Open PDF directly from memory
    # ---------------------------------

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if pdf.needs_pass:

        if not pdf.authenticate(
            settings.PDF_PASSWORD
        ):

            pdf.close()

            raise ValueError(
                "Invalid PDF password"
            )


    # ---------------------------------
    # Extract full text
    # ---------------------------------

    full_text = ""

    for page in pdf:

        full_text += (
            page.get_text("text")
            + "\n"
        )

    pdf.close()


    # ---------------------------------
    # Keep only transaction section
    # ---------------------------------

    start = re.search(
        r"\d{2}-\d{2}-\d{4}",
        full_text
    )

    if not start:
        raise ValueError(
            "No transaction dates found"
        )


    end = full_text.find(
        "Account Related Other Information"
    )

    if end == -1:
        raise ValueError(
            "End marker not found"
        )


    transaction_text = full_text[
        start.start():end
    ]


    # ---------------------------------
    # Remove page footers
    # ---------------------------------

    transaction_text = re.sub(
        r"Page\s+\d+\s+of\s+\d+.*?\n",
        "\n",
        transaction_text
    )


    # ---------------------------------
    # Remove repeated page headers
    # ---------------------------------

    transaction_text = re.sub(
        r"Statement of Transactions.*?BALANCE\s*",
        "",
        transaction_text,
        flags=re.DOTALL
    )


    # ---------------------------------
    # Split transactions
    # ---------------------------------

    transactions = re.findall(
        r"\d{2}-\d{2}-\d{4}.*?"
        r"(?=\n\d{2}-\d{2}-\d{4}|\nTotal:|$)",
        transaction_text,
        flags=re.DOTALL
    )


    # ---------------------------------
    # Parse transactions
    # ---------------------------------

    records = []

    previous_balance = None

    amount_pattern = (
        r"\d{1,3}(?:,\d{3})*\.\d{2}"
    )


    for txn in transactions:

        txn = txn.strip()


        # -----------------------------
        # Date
        # -----------------------------

        date_match = re.match(
            r"(\d{2}-\d{2}-\d{4})",
            txn
        )

        if not date_match:
            continue

        date = date_match.group(1)


        # -----------------------------
        # Amounts
        # -----------------------------

        amounts = re.findall(
            amount_pattern,
            txn
        )

        amounts = [
            float(
                amount.replace(",", "")
            )
            for amount in amounts
        ]

        if not amounts:
            continue


        deposit = None
        withdrawal = None


        # -----------------------------
        # Opening Balance
        # -----------------------------

        if "B/F" in txn:

            balance = amounts[-1]

            records.append(
                {
                    "date": date,
                    "particulars": "B/F",
                    "note": None,
                    "deposit": None,
                    "withdrawal": None,
                    "balance": balance
                }
            )

            previous_balance = balance

            continue


        # -----------------------------
        # Transaction Amount + Balance
        # -----------------------------

        balance = amounts[-1]

        txn_amount = amounts[-2]


        if previous_balance is not None:

            diff = round(
                balance - previous_balance,
                2
            )

            if diff > 0:
                deposit = txn_amount

            elif diff < 0:
                withdrawal = txn_amount


        # -----------------------------
        # Particulars
        # -----------------------------

        particulars = re.sub(
            amount_pattern,
            "",
            txn
        )

        particulars = particulars.replace(
            date,
            ""
        ).strip()

        particulars = re.sub(
            r"\s+",
            " ",
            particulars
        ).strip()


        # -----------------------------
        # Merchant
        # -----------------------------

        merchant = extract_merchant(
            particulars
        )


        # -----------------------------
        # Note
        # -----------------------------

        note = extract_note(
            particulars
        )


        # -----------------------------
        # Save record
        # -----------------------------

        records.append(
            {
                "date": date,
                "particulars": particulars,
                "merchant": merchant,
                "note": note,
                "deposit": deposit,
                "withdrawal": withdrawal,
                "balance": balance
            }
        )

        previous_balance = balance


    # ---------------------------------
    # DataFrame
    # ---------------------------------

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError(
            "No transactions extracted"
        )


    # ---------------------------------
    # Monthly Summary
    # ---------------------------------

    opening_balance = df.iloc[0]["balance"]

    closing_balance = df.iloc[-1]["balance"]

    income = (
        df["deposit"]
        .fillna(0)
        .sum()
    )

    expenses = (
        df["withdrawal"]
        .fillna(0)
        .sum()
    )

    saved = income - expenses

    income_count = (
        df["deposit"]
        .notna()
        .sum()
    )

    expense_count = (
        df["withdrawal"]
        .notna()
        .sum()
    )


    # ---------------------------------
    # Expense DataFrame
    # ---------------------------------

    expense_df = df[
        df["withdrawal"].notna()
    ].copy()


    # ---------------------------------
    # Category
    # ---------------------------------

    expense_df["category"] = (
        expense_df.apply(
            lambda row:
                row["note"]
                if pd.notna(row["note"])
                else row["merchant"],
            axis=1
        )
    )


    # ---------------------------------
    # Category Summary
    # ---------------------------------

    category_summary = (
        expense_df
        .groupby("category")["withdrawal"]
        .sum()
        .sort_values(ascending=False)
    )


    # ---------------------------------
    # Top 5 Expenses
    # ---------------------------------

    top_5_expenses = (
        expense_df
        .sort_values(
            "withdrawal",
            ascending=False
        )
        [
            [
                "category",
                "withdrawal"
            ]
        ]
        .head(5)
    )


    # ---------------------------------
    # Build Summary
    # ---------------------------------

    summary = {

        "opening_balance":
            round(float(opening_balance), 2),

        "income":
            round(float(income), 2),

        "expenses":
            round(float(expenses), 2),

        "saved":
            round(float(saved), 2),

        "closing_balance":
            round(float(closing_balance), 2),

        "income_count":
            int(income_count),

        "expense_count":
            int(expense_count),

        "top_5_expenses": [

            {
                "category":
                    row["category"],

                "amount":
                    round(
                        float(
                            row["withdrawal"]
                        ),
                        2
                    )
            }

            for _, row
            in top_5_expenses.iterrows()
        ],

        "category_summary": {

            str(category):
                round(
                    float(amount),
                    2
                )

            for category, amount
            in category_summary.items()
        }
    }


    return summary