from fastapi import APIRouter , HTTPException
from app.payments.client import client
router = APIRouter()
import hmac
import hashlib




@router.post("/create-order")
def create_order(amount: int):

    order = client.order.create({
        "amount": amount * 100,  
        "currency": "INR"
    })

    return {
        "order_id": order["id"],
        "amount": order["amount"]
    }
    
    

@router.post("/verify")
def verify_payment(data: dict):

    generated_signature = hmac.new(
        b"YOUR_SECRET",
        f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != data["razorpay_signature"]:
        raise HTTPException(status_code=400, detail="Payment failed")

    return {"status": "Payment verified ✅"}