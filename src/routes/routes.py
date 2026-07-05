from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from src.models.models import (
    UploadPdfResponse
)

from src.service.service import (
    StatementService
)


router = APIRouter()


statement_service = (
    StatementService()
)


@router.post(
    "/upload-pdf",
    response_model=UploadPdfResponse
)
async def upload_pdf(

    file: UploadFile = File(...),

    email_subject: str = Form(...),

    email_date: str = Form(...),

    gmail_message_id: str = Form(...)

):

    # ---------------------------------
    # Read PDF into memory
    # ---------------------------------

    pdf_bytes = await file.read()


    # ---------------------------------
    # Call Service Layer
    # ---------------------------------

    result = (
        await statement_service
        .process_statement(
            pdf_bytes
        )
    )


    telegram_response = (
        result[
            "telegram_response"
        ]
    )


    # ---------------------------------
    # Response
    # ---------------------------------

    return {

        "status":
            "success",

        "message":
            "PDF processed and summary sent to Telegram",

        "filename":
            file.filename,

        "summary":
            result["summary"],

        "telegram_message_id":

            telegram_response[
                "result"
            ][
                "message_id"
            ]

    }