from pydantic import BaseModel
from typing import List, Dict


class ReportRequest(BaseModel):
    report_type: str
    start_date: str
    end_date: str

class ReportResponse(BaseModel):
    report_type: str
    total_recorsds: int
    data: List[Dict]    