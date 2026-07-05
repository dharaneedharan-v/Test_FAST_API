# # from fastapi import FastAPI, UploadFile, File, Form

# # app = FastAPI()


# # @app.get("/")
# # def root():
# #     return {
# #         "message": "Hello World"
# #     }


# # @app.post("/upload-pdf")
# # async def upload_pdf(
# #     file: UploadFile = File(...),
# #     email_subject: str = Form(...),
# #     email_date: str = Form(...),
# #     gmail_message_id: str = Form(...)
# # ):

# #     pdf_bytes = await file.read()

# #     print("PDF RECEIVED")
# #     print("Filename:", file.filename)
# #     print("Size:", len(pdf_bytes))
# #     print("Subject:", email_subject)
# #     print("Email Date:", email_date)
# #     print("Gmail Message ID:", gmail_message_id)

# #     return {
# #         "status": "success",
# #         "filename": file.filename,
# #         "size_bytes": len(pdf_bytes),
# #         "email_subject": email_subject,
# #         "email_date": email_date,
# #         "gmail_message_id": gmail_message_id
# #     }



# import fitz
# import re
# import pandas as pd

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException


# app = FastAPI()


# PDF_PASSWORD = "dhar2208"


# @app.get("/")
# def root():
#     return {
#         "message": "Hello World"
#     }


# @app.post("/upload-pdf")
# async def upload_pdf(
#     file: UploadFile = File(...),
#     email_subject: str = Form(...),
#     email_date: str = Form(...),
#     gmail_message_id: str = Form(...)
# ):

#     try:

#         # ============================================================
#         # 1. VALIDATE PDF
#         # ============================================================

#         if not file.filename.lower().endswith(".pdf"):

#             raise HTTPException(
#                 status_code=400,
#                 detail="Only PDF files are allowed"
#             )


#         # ============================================================
#         # 2. READ PDF FROM REQUEST
#         # ============================================================

#         pdf_bytes = await file.read()

#         print("PDF RECEIVED")
#         print("Filename:", file.filename)
#         print("Size:", len(pdf_bytes))
#         print("Subject:", email_subject)
#         print("Email Date:", email_date)
#         print("Gmail Message ID:", gmail_message_id)


#         # ============================================================
#         # 3. OPEN PDF DIRECTLY FROM MEMORY
#         # ============================================================

#         pdf = fitz.open(
#             stream=pdf_bytes,
#             filetype="pdf"
#         )


#         # ============================================================
#         # 4. UNLOCK PASSWORD-PROTECTED PDF
#         # ============================================================

#         if pdf.needs_pass:

#             authenticated = pdf.authenticate(
#                 PDF_PASSWORD
#             )

#             if not authenticated:

#                 pdf.close()

#                 raise HTTPException(
#                     status_code=400,
#                     detail="Invalid PDF password"
#                 )


#         # ============================================================
#         # 5. EXTRACT FULL TEXT
#         # ============================================================

#         full_text = ""

#         for page in pdf:

#             full_text += (
#                 page.get_text("text")
#                 + "\n"
#             )


#         pdf.close()


#         # ============================================================
#         # 6. FIND TRANSACTION SECTION
#         # ============================================================

#         start = re.search(
#             r"\d{2}-\d{2}-\d{4}",
#             full_text
#         )


#         if not start:

#             raise HTTPException(
#                 status_code=422,
#                 detail="No transaction dates found"
#             )


#         end = full_text.find(
#             "Account Related Other Information"
#         )


#         if end == -1:

#             raise HTTPException(
#                 status_code=422,
#                 detail="Transaction end marker not found"
#             )


#         transaction_text = full_text[
#             start.start():end
#         ]


#         # ============================================================
#         # 7. REMOVE PAGE FOOTERS
#         # ============================================================

#         transaction_text = re.sub(
#             r"Page\s+\d+\s+of\s+\d+.*?\n",
#             "\n",
#             transaction_text
#         )


#         # ============================================================
#         # 8. REMOVE REPEATED HEADERS
#         # ============================================================

#         transaction_text = re.sub(
#             r"Statement of Transactions.*?BALANCE\s*",
#             "",
#             transaction_text,
#             flags=re.DOTALL
#         )


#         # ============================================================
#         # 9. SPLIT TRANSACTIONS
#         # ============================================================

#         transactions = re.findall(

#             r"\d{2}-\d{2}-\d{4}.*?"
#             r"(?=\n\d{2}-\d{2}-\d{4}|\nTotal:|$)",

#             transaction_text,

#             flags=re.DOTALL
#         )


#         print(
#             "Transactions Found:",
#             len(transactions)
#         )


#         # ============================================================
#         # 10. HELPER: EXTRACT NOTE
#         # ============================================================

#         def extract_note(particulars):

#             match = re.search(

#                 r"UPI/[^/]+/[^/]+/([^/]+)/",

#                 particulars,

#                 re.IGNORECASE
#             )


#             if not match:

#                 return None


#             note = match.group(1).strip()


#             ignore_values = {

#                 "",

#                 "UPI",

#                 "PAY",

#                 "PAYMENT",

#                 "UPI PAYMENT"
#             }


#             if note.upper() in ignore_values:

#                 return None


#             return note


#         # ============================================================
#         # 11. HELPER: EXTRACT MERCHANT
#         # ============================================================

#         def extract_merchant(particulars):

#             if "/" in particulars:

#                 return (
#                     particulars
#                     .split("/")[0]
#                     .strip()
#                 )


#             return particulars.strip()


#         # ============================================================
#         # 12. PARSE TRANSACTIONS
#         # ============================================================

#         records = []

#         previous_balance = None


#         amount_pattern = (
#             r"\d{1,3}"
#             r"(?:,\d{3})*"
#             r"\.\d{2}"
#         )


#         for txn in transactions:

#             txn = txn.strip()


#             # --------------------------------------------------------
#             # DATE
#             # --------------------------------------------------------

#             date_match = re.match(

#                 r"(\d{2}-\d{2}-\d{4})",

#                 txn
#             )


#             if not date_match:

#                 continue


#             date = date_match.group(1)


#             # --------------------------------------------------------
#             # AMOUNTS
#             # --------------------------------------------------------

#             amounts = re.findall(

#                 amount_pattern,

#                 txn
#             )


#             amounts = [

#                 float(
#                     amount.replace(",", "")
#                 )

#                 for amount in amounts
#             ]


#             if not amounts:

#                 continue


#             deposit = None

#             withdrawal = None


#             # --------------------------------------------------------
#             # OPENING BALANCE
#             # --------------------------------------------------------

#             if "B/F" in txn:

#                 balance = amounts[-1]


#                 records.append({

#                     "date": date,

#                     "particulars": "B/F",

#                     "merchant": "B/F",

#                     "note": None,

#                     "deposit": None,

#                     "withdrawal": None,

#                     "balance": balance

#                 })


#                 previous_balance = balance

#                 continue


#             # --------------------------------------------------------
#             # NEED AT LEAST:
#             #
#             # transaction amount
#             # balance
#             # --------------------------------------------------------

#             if len(amounts) < 2:

#                 print(
#                     "Skipping transaction "
#                     "with insufficient amounts:",
#                     txn
#                 )

#                 continue


#             # --------------------------------------------------------
#             # TRANSACTION AMOUNT + BALANCE
#             # --------------------------------------------------------

#             balance = amounts[-1]

#             txn_amount = amounts[-2]


#             if previous_balance is not None:

#                 diff = round(

#                     balance
#                     - previous_balance,

#                     2
#                 )


#                 if diff > 0:

#                     deposit = txn_amount


#                 elif diff < 0:

#                     withdrawal = txn_amount


#             # --------------------------------------------------------
#             # PARTICULARS
#             # --------------------------------------------------------

#             particulars = re.sub(

#                 amount_pattern,

#                 "",

#                 txn
#             )


#             particulars = particulars.replace(

#                 date,

#                 ""

#             ).strip()


#             particulars = re.sub(

#                 r"\s+",

#                 " ",

#                 particulars

#             ).strip()


#             # --------------------------------------------------------
#             # MERCHANT
#             # --------------------------------------------------------

#             merchant = extract_merchant(
#                 particulars
#             )


#             # --------------------------------------------------------
#             # NOTE
#             # --------------------------------------------------------

#             note = extract_note(
#                 particulars
#             )


#             # --------------------------------------------------------
#             # SAVE RECORD
#             # --------------------------------------------------------

#             records.append({

#                 "date": date,

#                 "particulars": particulars,

#                 "merchant": merchant,

#                 "note": note,

#                 "deposit": deposit,

#                 "withdrawal": withdrawal,

#                 "balance": balance

#             })


#             previous_balance = balance


#         # ============================================================
#         # 13. VALIDATE RECORDS
#         # ============================================================

#         if not records:

#             raise HTTPException(

#                 status_code=422,

#                 detail="No transactions extracted"

#             )


#         # ============================================================
#         # 14. CREATE DATAFRAME
#         # ============================================================

#         df = pd.DataFrame(records)


#         # ============================================================
#         # 15. MONTHLY SUMMARY
#         # ============================================================

#         opening_balance = float(
#             df.iloc[0]["balance"]
#         )


#         closing_balance = float(
#             df.iloc[-1]["balance"]
#         )


#         income = float(

#             df["deposit"]
#             .fillna(0)
#             .sum()

#         )


#         expenses = float(

#             df["withdrawal"]
#             .fillna(0)
#             .sum()

#         )


#         saved = income - expenses


#         income_count = int(

#             df["deposit"]
#             .notna()
#             .sum()

#         )


#         expense_count = int(

#             df["withdrawal"]
#             .notna()
#             .sum()

#         )


#         # ============================================================
#         # 16. EXPENSE DATAFRAME
#         # ============================================================

#         expense_df = df[

#             df["withdrawal"].notna()

#         ].copy()


#         # ============================================================
#         # 17. CATEGORY
#         # ============================================================

#         expense_df["category"] = (

#             expense_df.apply(

#                 lambda row:

#                     row["note"]

#                     if pd.notna(row["note"])

#                     else row["merchant"],

#                 axis=1
#             )

#         )


#         # ============================================================
#         # 18. CATEGORY SUMMARY
#         # ============================================================

#         category_summary = (

#             expense_df

#             .groupby("category")[

#                 "withdrawal"

#             ]

#             .sum()

#             .sort_values(

#                 ascending=False

#             )

#         )


#         # ============================================================
#         # 19. TOP 5 EXPENSES
#         # ============================================================

#         top_5_expenses = (

#             expense_df

#             .sort_values(

#                 "withdrawal",

#                 ascending=False

#             )

#             [[

#                 "category",

#                 "withdrawal"

#             ]]

#             .head(5)

#         )


#         # ============================================================
#         # 20. BUILD SUMMARY
#         # ============================================================

#         summary = {

#             "opening_balance":
#                 round(opening_balance, 2),

#             "income":
#                 round(income, 2),

#             "expenses":
#                 round(expenses, 2),

#             "saved":
#                 round(saved, 2),

#             "closing_balance":
#                 round(closing_balance, 2),

#             "income_count":
#                 income_count,

#             "expense_count":
#                 expense_count,


#             "top_5_expenses": [

#                 {

#                     "category":
#                         row["category"],

#                     "amount":
#                         round(

#                             float(
#                                 row["withdrawal"]
#                             ),

#                             2
#                         )

#                 }

#                 for _, row

#                 in top_5_expenses.iterrows()

#             ],


#             "category_summary": {

#                 str(category):

#                     round(

#                         float(amount),

#                         2
#                     )

#                 for category, amount

#                 in category_summary.items()

#             }

#         }


#         # ============================================================
#         # 21. CONVERT TRANSACTIONS TO JSON-SAFE RECORDS
#         # ============================================================

#         transaction_records = (

#             df

#             .where(
#                 pd.notnull(df),
#                 None
#             )

#             .to_dict(
#                 orient="records"
#             )

#         )


#         # ============================================================
#         # 22. RETURN RESPONSE
#         # ============================================================

#         return {

#             "status": "success",

#             "message":
#                 "PDF processed successfully",

#             "file": {

#                 "filename":
#                     file.filename,

#                 "size_bytes":
#                     len(pdf_bytes)

#             },


#             "email": {

#                 "subject":
#                     email_subject,

#                 "date":
#                     email_date,

#                 "gmail_message_id":
#                     gmail_message_id

#             },


#             "transactions_found":
#                 len(transaction_records),


#             "transactions":
#                 transaction_records,


#             "summary":
#                 summary

#         }


#     except HTTPException:

#         raise


#     except Exception as error:

#         print(
#             "PROCESSING ERROR:",
#             str(error)
#         )


#         raise HTTPException(

#             status_code=500,

#             detail=str(error)

#         )



from fastapi import FastAPI

from src.routes.routes import router


app = FastAPI(
    title="ICICI Statement Processor"
)


app.include_router(
    router
)


@app.get("/")
def root():

    return {
        "message":
            "ICICI Statement Processor API running"
    }



    

# #  help full commands 
# # To run the application: 
#             # uv run uvicorn main:app --reload

#         # uv export --no-hashes --no-dev --format requirements-txt > requirements.txt



