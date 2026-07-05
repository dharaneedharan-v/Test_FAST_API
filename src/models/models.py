from typing import Dict, List

from pydantic import BaseModel


class TopExpense(BaseModel):

    category: str

    amount: float


class SummaryResponse(BaseModel):

    opening_balance: float

    income: float

    expenses: float

    saved: float

    closing_balance: float

    income_count: int

    expense_count: int

    top_5_expenses: List[TopExpense]

    category_summary: Dict[str, float]


class UploadPdfResponse(BaseModel):

    status: str

    message: str

    filename: str

    summary: SummaryResponse

    telegram_message_id: int