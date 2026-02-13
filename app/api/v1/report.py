from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.services.report_service import ReportService
from app.api.dependency import get_report_service
from app.schemas.report import ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/{report_type}",
    status_code=status.HTTP_200_OK,
    response_model=ReportResponse
)
def generate_report(
    report_type: str = Path(..., description="Type of report to generate" , example=['users', 'bookings', 'payments']),
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: date = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service)
):
    try:
        result = report_service.generate_report(
            db=db,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )

        return {
            'report_type': report_type,
            "total_recorsds": len(result),
            "data": result
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{report_type}/pdf")
def download_pdf_report(
    report_type: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service)
):
    return report_service.generate_report_pdf(
        db=db,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{report_type}/excel")
def download_excel_report(
    report_type: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service)
):
    return report_service.generate_report_excel(
        db=db,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date
    )