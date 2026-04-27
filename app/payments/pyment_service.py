
import hmac
import hashlib
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.booking import Booking
from app.payments.client import client

class PaymentService:

    def __init__(self):
        self.client = client
        
        
    def create_order(self, db: Session, booking: Booking, amount: int):
       
        order = self.client.order.create({
            "amount": amount * 100,
            "currency": "INR"
        })

        
        payment = Payment(
            booking_id=booking.id,
            user_id=booking.user_id,
            amount=amount * 100,
            provider_order_id=order["id"],
            status="CREATED"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "order_id": order["id"],
            "amount": amount
        }

    def verify_payment(self, db: Session, data: dict):
        generated_signature = hmac.new(
            b"YOUR_KEY_SECRET",
            (data["razorpay_order_id"] + "|" + data["razorpay_payment_id"]).encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != data["razorpay_signature"]:
            raise HTTPException(status_code=400, detail="Invalid payment")

        # 🔥 Step 1: update payment
        payment = db.query(Payment).filter(
            Payment.provider_order_id == data["razorpay_order_id"]
        ).first()

        if not payment:
            raise HTTPException(404, "Payment not found")

        payment.status = "SUCCESS"
        payment.provider_payment_id = data["razorpay_payment_id"]

        # 🔥 Step 2: activate booking
        booking = db.query(Booking).filter(
            Booking.id == payment.booking_id
        ).first()

        booking.status = "ACTIVE"

        db.commit()

        return {"message": "Payment verified & booking activated"}