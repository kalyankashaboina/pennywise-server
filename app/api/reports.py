from fastapi import APIRouter, Depends, BackgroundTasks
from app.dependencies.auth import get_current_user
from app.tasks.report_tasks import ReportTasks

router = APIRouter()
tasks = ReportTasks()


@router.post("/monthly")
async def generate_monthly_report(
    month: str,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    background_tasks.add_task(
        tasks.generate_monthly_report,
        user_id=current_user.id,
        month=month,
        output_dir="/tmp/reports",
    )

    return {
        "success": True,
        "message": "Report generation started",
    }
