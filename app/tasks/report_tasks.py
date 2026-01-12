from pathlib import Path

from app.services.audit_service import AuditService
from app.services.report_service import ReportService
from app.services.transaction_service import TransactionService
from app.utils.logger import get_logger

logger = get_logger("pennywise.tasks.reports")


class ReportTasks:
    def __init__(self):
        self.tx_service = TransactionService()
        self.report_service = ReportService()
        self.audit = AuditService()

    async def generate_monthly_report(
        self,
        *,
        user_id: str,
        month: str,
        output_dir: str,
        request=None,
    ):
        logger.info(
            "REPORT_TASK_STARTED",
            extra={"user_id": user_id, "month": month},
        )

        try:
            transactions = await self.tx_service.list_for_month(
                user_id=user_id,
                month=month,
            )

            Path(output_dir).mkdir(parents=True, exist_ok=True)
            output_path = Path(output_dir) / f"pennywise-{user_id}-{month}.pdf"

            # ✅ FIXED - Now using async method
            await self.report_service.generate_transaction_report(
                user_id=user_id,
                transactions=[t.dict() for t in transactions],
                title="Monthly Statement",
                period_label=month,
                output_path=str(output_path),
            )

            await self.audit.log(
                action="REPORT_GENERATED",
                user_id=user_id,
                entity="report",
                entity_id=str(output_path),
                metadata={
                    "month": month,
                    "transaction_count": len(transactions),
                },
                request=request,
            )

            logger.info(
                "REPORT_TASK_COMPLETED",
                extra={"user_id": user_id, "path": str(output_path)},
            )

        except Exception as exc:
            logger.exception(
                "REPORT_TASK_FAILED",
                extra={"user_id": user_id, "month": month},
            )

            await self.audit.log(
                action="REPORT_FAILED",
                user_id=user_id,
                entity="report",
                metadata={
                    "month": month,
                    "error": str(exc),
                },
                request=request,
            )
