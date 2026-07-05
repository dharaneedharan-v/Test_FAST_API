from src.client.telegram import (
    TelegramClient
)

from src.utils.helpers import (
    process_pdf
)


class StatementService:

    def __init__(self):

        self.telegram_client = (
            TelegramClient()
        )


    async def process_statement(
        self,
        pdf_bytes: bytes
    ):

        # ---------------------------------
        # Process PDF
        # ---------------------------------

        summary = process_pdf(
            pdf_bytes
        )


        # ---------------------------------
        # Build Telegram message
        # ---------------------------------

        telegram_message = (
            self._build_telegram_message(
                summary
            )
        )


        # ---------------------------------
        # Send Telegram message
        # ---------------------------------

        telegram_response = (
            await self.telegram_client
            .send_message(
                telegram_message
            )
        )


        # ---------------------------------
        # Return result
        # ---------------------------------

        return {

            "summary":
                summary,

            "telegram_response":
                telegram_response

        }


    def _build_telegram_message(
        self,
        summary
    ):

        message = (

            "📊 MONTHLY SUMMARY\n\n"

            f"Opening Balance : "
            f"₹{summary['opening_balance']:,.2f}\n"

            f"Income          : "
            f"₹{summary['income']:,.2f}\n"

            f"Expenses        : "
            f"₹{summary['expenses']:,.2f}\n"

            f"Saved           : "
            f"₹{summary['saved']:,.2f}\n"

            f"Closing Balance : "
            f"₹{summary['closing_balance']:,.2f}\n"

            "\n💳 BRIEF\n\n"

            f"Spend / Withdrawals : "
            f"{summary['expense_count']}\n"

            f"Income Transactions : "
            f"{summary['income_count']}\n"

            "\n🔥 TOP 5 EXPENSES\n"

        )


        for index, expense in enumerate(
            summary["top_5_expenses"],
            start=1
        ):

            message += (

                f"\n{index}. "

                f"{expense['category']} - "

                f"₹{expense['amount']:,.2f}"

            )


        message += (
            "\n\n🏷 SPEND GROUPED BY TAG\n"
        )


        for category, amount in (
            summary[
                "category_summary"
            ].items()
        ):

            message += (

                f"\n{category} : "

                f"₹{amount:,.2f}"

            )


        return message