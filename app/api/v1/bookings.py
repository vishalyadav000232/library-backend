from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def book_seat():
    return {"message": "Seat booked"}
