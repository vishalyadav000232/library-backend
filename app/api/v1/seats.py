# app/api/v1/seats.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List , Dict
from uuid import UUID
from app.schemas.seats import SeatCreate, SeatResponse , SeatUpdate
from app.services.seat_services import create_seat
from app.database.db import get_db
from app.models.seats import Seat  
from app.api.admin.admin_gaurd import admin_required
from sqlalchemy import func

router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)


@router.post(
    "/",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED
)

def add_seat(seat: SeatCreate, db: Session = Depends(get_db) , admin = Depends(admin_required)):
    try:
        new_seat = create_seat(db, seat)
        return new_seat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.delete(
    "/{seat_id}/delete",
    status_code=status.HTTP_200_OK
)
def del_seat(
    seat_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()

    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    db.delete(seat)
    db.commit()

    return {
        "message": f"Successfully deleted seat: {seat_id}"
    }

@router.get(
    "/",
    response_model=List[SeatResponse],
    status_code=status.HTTP_200_OK
)
def get_seats(db: Session = Depends(get_db)):
    seats = db.query(Seat).all()
    return seats


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK
)
def seat_stats(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    total = db.query(func.count(Seat.id)).scalar()

    active = db.query(func.count(Seat.id)).filter(
        Seat.is_active == True
    ).scalar()

    inactive = db.query(func.count(Seat.id)).filter(
        Seat.is_active == False
    ).scalar()


    return {
        "total": total,
        "active": active,
        "inactive": inactive,
       
        
    }


@router.patch("/{seat_id}/update", status_code=status.HTTP_200_OK)
def update_seat(seat_id :UUID ,update_data :SeatUpdate, db : Session = Depends(get_db) ,admin=Depends(admin_required)   ):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()

    if not update_seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="seat are not Found !"
        )
    
    if update_data.seat_number is not None:
        seat.seat_number = update_data.seat_number

    if update_data.is_active is not None:
        seat.is_active = update_data.is_active

    db.commit()
    db.refresh(seat)


    return { 
        "message": "Seat updated successfully",
        "data": seat
    }

