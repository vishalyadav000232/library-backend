from fastapi import APIRouter

router = APIRouter()

@router.post("/pay")
def make_payment():
    return {"status": "Payment successful (mock)"}
