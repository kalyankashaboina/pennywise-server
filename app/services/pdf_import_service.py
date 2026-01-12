import re
from datetime import datetime
from typing import List

from pypdf import PdfReader

from app.errors.base import AppError
from app.errors.codes import ErrorCode
from app.utils.logger import get_logger

logger = get_logger("pennywise.pdf.phonepe")


class PhonePePdfParser:
    """
    PhonePe PDF parser (TEXT-based PDFs only).

    ❌ Encrypted PDFs → rejected
    ❌ Scanned PDFs (image-only) → rejected (OCR later)
    """

    AMOUNT_REGEX = re.compile(r"₹\s?([\d,]+(?:\.\d{1,2})?)")
    DATE_REGEX = re.compile(r"(\d{1,2}\s[A-Za-z]{3}\s\d{4})")

    def __init__(self, path: str):
        self.path = path

    # -------------------------------------------------
    # Extract raw text from PDF
    # -------------------------------------------------
    def _extract_text(self) -> str:
        try:
            reader = PdfReader(self.path)
        except Exception as e:
            logger.exception("Failed to open PDF")
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid or corrupted PDF file",
                status_code=400,
            ) from e

        if reader.is_encrypted:
            logger.warning("Encrypted PDF detected")
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="PDF is password protected",
                status_code=400,
            )

        text_parts: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        text = "\n".join(text_parts)

        if not text.strip():
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Scanned PDF not supported yet",
                status_code=400,
            )

        return text

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------
    def parse_transactions(self) -> List[dict]:
        raw_text = self._extract_text()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        transactions: list[dict] = []
        failed_lines = 0

        for line in lines:
            if not self._is_transaction_line(line):
                continue

            try:
                tx = self._parse_line(line)
                transactions.append(tx)
            except Exception as exc:
                failed_lines += 1
                logger.warning(
                    "Transaction parse failed",
                    extra={
                        "line": line,
                        "error": str(exc),
                    },
                )

        if not transactions:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="No transactions detected in PDF",
                status_code=400,
            )

        logger.info(
            "PhonePe PDF parsed successfully",
            extra={
                "total_lines": len(lines),
                "transactions": len(transactions),
                "failed_lines": failed_lines,
            },
        )

        return transactions

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def _is_transaction_line(self, line: str) -> bool:
        keywords = (
            "Paid",
            "Received",
            "Credited",
            "Debited",
            "UPI",
        )
        return "₹" in line and any(k in line for k in keywords)

    def _parse_line(self, line: str) -> dict:
        amount = self._extract_amount(line)
        tx_type = self._detect_type(line)
        date = self._extract_date(line)

        return {
            "date": date,
            "amount": amount,
            "type": tx_type,  # income | expense
            "description": line,
            "category": "phonepe",
            "source": "phonepe",
            "is_recurring": False,
        }

    def _extract_amount(self, text: str) -> float:
        match = self.AMOUNT_REGEX.search(text)
        if not match:
            raise ValueError("Amount not found")

        return float(match.group(1).replace(",", ""))

    def _detect_type(self, text: str) -> str:
        if any(k in text for k in ("Paid", "Debited")):
            return "expense"
        if any(k in text for k in ("Received", "Credited")):
            return "income"

        raise ValueError("Unable to determine transaction type")

    def _extract_date(self, text: str) -> datetime:
        match = self.DATE_REGEX.search(text)
        if not match:
            logger.debug(
                "Date not found in line, defaulting to current date",
                extra={"line": text},
            )
            return datetime.utcnow()

        try:
            return datetime.strptime(match.group(1), "%d %b %Y")
        except ValueError:
            return datetime.utcnow()
