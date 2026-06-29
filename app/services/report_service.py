import logging
from datetime import date, datetime
from io import BytesIO
from typing import Dict, List

import pandas as pd
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception.database import DatabaseException
from app.core.exception.reports import (
    EmptyReportDataException,
    InvalidReportDateRangeException,
    InvalidReportTypeException,
    ReportExportException,
    ReportGenerationException,
)
from app.repository.report_repoitory import (
    ReportFactoryInterface,
    ReportRepository,
)
from app.utils.pdf_generator import generate_professional_pdf


logger = logging.getLogger(__name__)


class ReportService:

    def __init__(self, factory: ReportFactoryInterface):
        self.factory = factory

    def generate_report(
        self,
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        try:
            logger.info(
                "Generating report. report_type=%s start_date=%s end_date=%s",
                report_type,
                start_date,
                end_date,
            )

            if not report_type:
                logger.warning("Report generation failed. Report type is missing.")
                raise InvalidReportTypeException()

            if start_date > end_date:
                logger.warning(
                    "Invalid report date range. start_date=%s end_date=%s",
                    start_date,
                    end_date,
                )
                raise InvalidReportDateRangeException()

            start = datetime.combine(start_date, datetime.min.time())
            end = datetime.combine(end_date, datetime.max.time())

            repository: ReportRepository = self.factory.get_report(report_type)

            data = repository.generate_report(db, start, end)

            if not data:
                logger.warning(
                    "Report generated with no data. report_type=%s start_date=%s end_date=%s",
                    report_type,
                    start_date,
                    end_date,
                )
                raise EmptyReportDataException()

            logger.info(
                "Report generated successfully. report_type=%s rows=%s",
                report_type,
                len(data),
            )

            return data

        except (
            InvalidReportTypeException,
            InvalidReportDateRangeException,
            EmptyReportDataException,
        ):
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while generating report. report_type=%s",
                report_type,
            )
            raise DatabaseException()

        except Exception:
            logger.exception(
                "Unexpected error while generating report. report_type=%s",
                report_type,
            )
            raise ReportGenerationException()

    def generate_report_pdf(
        self,
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date,
    ):
        try:
            logger.info(
                "Generating PDF report. report_type=%s start_date=%s end_date=%s",
                report_type,
                start_date,
                end_date,
            )

            data = self.generate_report(
                db=db,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
            )

            file_name = f"{report_type}_report_{start_date}_{end_date}.pdf"

            file_path = generate_professional_pdf(
                data=data,
                file_name=file_name,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
            )

            logger.info(
                "PDF report generated successfully. report_type=%s file_name=%s",
                report_type,
                file_name,
            )

            return FileResponse(
                file_path,
                media_type="application/pdf",
                filename=file_name,
            )

        except (
            InvalidReportTypeException,
            InvalidReportDateRangeException,
            EmptyReportDataException,
            DatabaseException,
            ReportGenerationException,
        ):
            raise

        except Exception:
            logger.exception(
                "Failed to export PDF report. report_type=%s",
                report_type,
            )
            raise ReportExportException()

    def generate_report_excel(
        self,
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date,
    ):
        try:
            logger.info(
                "Generating Excel report. report_type=%s start_date=%s end_date=%s",
                report_type,
                start_date,
                end_date,
            )

            data = self.generate_report(
                db=db,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
            )

            df = pd.DataFrame(data)

            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            file_name = f"{report_type}_report_{start_date}_{end_date}.xlsx"

            logger.info(
                "Excel report generated successfully. report_type=%s file_name=%s rows=%s",
                report_type,
                file_name,
                len(data),
            )

            return StreamingResponse(
                buffer,
                media_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                },
            )

        except (
            InvalidReportTypeException,
            InvalidReportDateRangeException,
            EmptyReportDataException,
            DatabaseException,
            ReportGenerationException,
        ):
            raise

        except Exception:
            logger.exception(
                "Failed to export Excel report. report_type=%s",
                report_type,
            )
            raise ReportExportException()