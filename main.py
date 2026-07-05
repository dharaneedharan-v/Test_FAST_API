from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Hello World"
    }


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    email_subject: str = Form(...),
    email_date: str = Form(...),
    gmail_message_id: str = Form(...)
):

    pdf_bytes = await file.read()

    print("PDF RECEIVED")
    print("Filename:", file.filename)
    print("Size:", len(pdf_bytes))
    print("Subject:", email_subject)
    print("Email Date:", email_date)
    print("Gmail Message ID:", gmail_message_id)

    return {
        "status": "success",
        "filename": file.filename,
        "size_bytes": len(pdf_bytes),
        "email_subject": email_subject,
        "email_date": email_date,
        "gmail_message_id": gmail_message_id
    }




#  help full commands 
# To run the application: 
            # uv run uvicorn main:app --reload

        # uv export --no-hashes --no-dev --format requirements-txt > requirements.txt
