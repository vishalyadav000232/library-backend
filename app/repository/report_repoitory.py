from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from typing import List, Dict

class ReportRepository(ABC):
    @abstractmethod
    def generate_report(self, db: Session,  start_date: datetime, end_date: datetime) -> List[Dict]:
        pass


class UserReportRepository(ReportRepository):

    def generate_report(self, db: Session, start_date: datetime, end_date: datetime) -> List[Dict]:
        users = db.query(User).filter(
            User.create_at >= start_date,
            User.create_at <= end_date
        ).all()

        return [{
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "create_at": user.create_at.isoformat()
        } for user in users
        ]


class BookingReportRepository(ReportRepository):
    def generate_report(self, db: Session, start_date: datetime, end_date: datetime) -> List[Dict]:
        bookings = db.query(Booking).filter(
            Booking.start_date >= start_date,
            Booking.start_date <= end_date
        ).all()

        return [
            {
                "id": str(b.id),
                "user_id": str(b.user_id),
                "seat_id": str(b.seat_id),
                "shift_id": str(b.shift_id),
                "start_date": b.start_date.isoformat(),
                "end_date": b.end_date.isoformat() if b.end_date else None,
                "status": b.status,
                "is_active": b.is_active
            }
            for b in bookings
        ]


class PaymentReportRepository (ReportRepository):
    def generate_report(self, db: Session,  start_date: datetime, end_date: datetime) -> List[Dict]:

        payments = db.query(Payment).filter(
            Payment.created_at >= start_date,
            Payment.created_at <= end_date
        ).all()

        return [
            {
                "id": str(p.id),
                "booking_id": str(p.booking_id),
                "amount": p.amount,
                "status": p.status,
                "provider": p.provider,
                "provider_payment_id": p.provider_payment_id
            }
            for p in payments
        ]



class ReportFactoryInterface(ABC):

    @abstractmethod
    def get_report(self, report_type: str) -> ReportRepository:
        pass



class ReportFactory(ReportFactoryInterface):

    REPORTS = {
        "users": UserReportRepository,
        "bookings": BookingReportRepository,
        "payments": PaymentReportRepository
    }

    def get_report(self, report_type: str) -> ReportRepository:
        report_class = self.REPORTS.get(report_type)

        if not report_class:
            raise ValueError("Invalid report type")

        return report_class()
