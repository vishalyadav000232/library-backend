from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from app.database.db import get_db
# from app.services.shift_services import create_shift
from datetime import time
from app.models.shift import Shift
router = APIRouter()

@router.post("/shifts", status_code=status.HTTP_201_CREATED ,)
def create_shift_endpoint(name: str, start_time: str, end_time: str, db: Session = Depends(get_db)):
   
    try:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM.")

    try:
        shift = create_shift(db, name, start, end)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Shift created successfully!", "shift_id": str(shift.id)}


@router.get("/shift", status_code=status.HTTP_200_OK)
def get_all_shift(db: Session = Depends(get_db)):
    try:
        shifts = db.query(Shift).all()   # ✅ Shift model use karo
        return shifts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Something went wrong: {str(e)}"
        )