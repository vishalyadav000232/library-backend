
from datetime import datetime, date

def normalize_date(d):
    if isinstance(d, datetime):
        return d.date()
    return d
