from datetime import datetime, date
from sqlalchemy.orm import Session
from typing import List, Dict
from app.utils.pdf_generator import generate_professional_pdf
from app.repository.report_repoitory import (
    ReportFactoryInterface,
    ReportRepository
)
from fastapi.responses import FileResponse
import os

class ReportService:

    def __init__(self, factory: ReportFactoryInterface):
        self.factory = factory

    def generate_report(
        self,
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:

        if not report_type:
            raise ValueError("Report type is required")

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        # Convert date → datetime for DB filtering
        start = datetime.combine(start_date, datetime.min.time())
        end = datetime.combine(end_date, datetime.max.time())

        repository: ReportRepository = self.factory.get_report(report_type)

        return repository.generate_report(db, start, end)
    
    def generate_report_pdf(
        self,
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date
    ):
        data = self.generate_report(db , report_type , start_date , end_date)

        
        
        file_name = f"{report_type}_report_{start_date}_{end_date}.pdf"

        file_path = generate_professional_pdf(data , file_name , report_type , start_date , end_date)

        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=file_name
        )
