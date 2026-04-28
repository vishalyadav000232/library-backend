from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.booking import Booking
from app.utils.booking_utils import normalize_date
from app.repository.booking_repository import BookingRepository , BookingRepositoryBase
import uuid
from abc import ABC , abstractmethod
from app.schemas.booking import BookingReport
from app.repository.seat_repository import SeatRepository
from app.websockets.manger import manager
import os
from app.models.payment import Payment , PaymentStatus

from app.payments.client import client


import hmac
import hashlib


from app.redis.bookings_lock import lock_seat , unlock_seat




class BookingServiceBase(ABC):
    
    @abstractmethod
    def create_booking(self, db: Session, booking_data):
        pass

    @abstractmethod
    def get_all_bookings(self, db: Session):
        pass

    @abstractmethod
    def get_booking_by_id(self, db: Session, booking_id):
        pass

    @abstractmethod
    def cancel_booking(self, db: Session, booking_id):
        pass
    
    @abstractmethod
    def my_bookings(self, db: Session, user_id):
        pass

    @abstractmethod
    def get_booking_report(self , db :Session):
        pass


class BookingService(BookingServiceBase):

    def __init__(self, repo: BookingRepositoryBase):
        self.repo = repo
        self.seat_repo = SeatRepository()

    async def create_booking(self, db: Session, booking_data):
        start_date = normalize_date(booking_data.start_date)
        end_date = normalize_date(booking_data.end_date)
        
        
        locked = lock_seat(
            booking_data.seat_id,
            booking_data.shift_id,
            start_date
        ) 
        
        if not locked:
            raise HTTPException(409, "Seat is temporarily locked")

        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date cannot be less than start_date"
            )

        if not   self.repo.is_seat_available(
            db,
            booking_data.seat_id,
            booking_data.shift_id,
            start_date
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seat already booked for this shift"
            )

        booking = Booking(
            id=uuid.uuid4(),
            user_id=booking_data.user_id,
            seat_id=booking_data.seat_id,
            shift_id=booking_data.shift_id,
            start_date=start_date,
            end_date=end_date,
            status="PENDING"
        )

        try:
           
            saved_booking =   self.repo.create(db, booking)

          
            # total_available =  self.seat_repo.get_available_seat_count(db)

            await manager.broadcast({
                "type": "SEAT_UPDATE",
                "seat_id": booking_data.seat_id,
                 "status": "LOCKED"
            })

            return saved_booking

        except IntegrityError:
            db.rollback()
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat already booked (race condition)"
        )
            
            
            
    def get_all_bookings(self, db: Session):
        return self.repo.get_all_bookings(db)

    def get_booking_by_id(self, db: Session, booking_id):
        booking = self.repo.get_booking_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking

    def cancel_booking(self, db: Session, booking_id):
        booking = self.repo.get_booking_by_id(db, booking_id)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active bookings can be cancelled"
            )

        return self.repo.update_booking_status(
            db,
            booking,
            "CANCELLED"
        )
    
    def my_bookings(self, db: Session, user_id):   
        return self.repo.my_booking(db, user_id)  

    def get_booking_report(self , db :Session):
        rows = self.repo.get_full_booking_data(db)


        result = []

        for booking , user , seat , payment  , shift in rows:
            result.append(
                    BookingReport(
                    booking_id=booking.id,
                    booking_date=booking.start_date,
                    status=booking.status,
                    user={
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    },
                    seat={
                        "seat_number": seat.seat_number,
                        "floor": seat.floor,
                        "amount": seat.price
                    },
                    payment={
                        "amount": payment.amount if payment else None,
                        "status": payment.status if payment else "pending"
                    },
                    shift= {
                        "name" : shift.name,
                        "start_time" : shift.start_time,
                        "end_time" : shift.end_time
                    }



                    

                )
            )

        return result
    
    
    async def confirm_booking_after_payment(self, db: Session, booking_id):

        booking = self.repo.get_booking_by_id(db, booking_id)

        if not booking:
            raise HTTPException(404, "Booking not found")

        booking.status = "CONFIRMED"

        db.commit()

      
        unlock_seat(
            booking.seat_id,
            booking.shift_id,
            booking.start_date
        )

       
        await manager.broadcast({
            "type": "SEAT_UPDATE",
            "seat_id": booking.seat_id,
            "status": "BOOKED"
        })

        return booking
    
    
    async def create_booking_with_payment(self, db: Session, booking_data, user_id):

       
        booking_data.user_id = user_id
        booking = await self.create_booking(db, booking_data)

       
        seat = self.seat_repo.get_by_id(db, booking.seat_id)
        amount = seat.price

        

       
        order = client.order.create({
            "amount": amount * 100,
            "currency": "INR"
        })

        payment = Payment(
            user_id=user_id,
            booking_id=booking.id,
            amount=amount,
            provider_order_id=order["id"],
            status=PaymentStatus.CREATED
        )

        db.add(payment)
        db.commit()

        return {
            "booking_id": str(booking.id),
            "order_id": order["id"],
            "amount": amount,
            "key": os.getenv("RAZORPAY_KEY_ID")
        }
        
    
    async def verify_payment(self, db: Session, data: dict):

        secret = os.getenv("RAZORPAY_KEY_SECRET")

        generated_signature = hmac.new(
            bytes(secret, "utf-8"),
            bytes(data["order_id"] + "|" + data["payment_id"], "utf-8"),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != data["signature"]:
            raise HTTPException(400, "Invalid payment")

        payment = db.query(Payment).filter(
            Payment.provider_order_id == data["order_id"]
        ).first()

        if not payment:
            raise HTTPException(404, "Payment not found")

        if payment.status == PaymentStatus.SUCCESS:
            return {"message": "Already processed"}

        payment.status = PaymentStatus.SUCCESS
        payment.provider_payment_id = data["payment_id"]

        booking = db.query(Booking).get(payment.booking_id)
        booking.status = "CONFIRMED"

        unlock_seat(
            booking.seat_id,
            booking.shift_id,
            booking.start_date
        )

        db.commit()

        await manager.broadcast({
            "type": "SEAT_UPDATE",
            "seat_id": booking.seat_id,
            "status": "BOOKED"
        })

        return {"message": "Payment success"}
                    
                            


