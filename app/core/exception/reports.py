from app.core.exception.base import AppException


class InvalidReportTypeException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid or missing report type.",
            status_code=400,
            error_code="INVALID_REPORT_TYPE",
        )


class InvalidReportDateRangeException(AppException):
    def __init__(self):
        super().__init__(
            message="Start date cannot be after end date.",
            status_code=400,
            error_code="INVALID_REPORT_DATE_RANGE",
        )


class EmptyReportDataException(AppException):
    def __init__(self):
        super().__init__(
            message="No report data found for the selected date range.",
            status_code=404,
            error_code="EMPTY_REPORT_DATA",
        )


class ReportGenerationException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to generate report.",
            status_code=500,
            error_code="REPORT_GENERATION_FAILED",
        )


class ReportExportException(AppException):
    def __init__(self):
        super().__init__(
            message="Failed to export report.",
            status_code=500,
            error_code="REPORT_EXPORT_FAILED",
        )