from sqlalchemy.orm import Session
from app.models.shift import Shift
import uuid

def create_shift(db: Session, name: str, start_time, end_time):
    """
    Create a new shift in the database.
    """
    # Check if shift name already exists
    existing_shift = db.query(Shift).filter(Shift.name == name).first()
    if existing_shift:
        raise Exception(f"Shift with name '{name}' already exists.")

    new_shift = Shift(
        id=uuid.uuid4(),
        name=name,
        start_time=start_time,
        end_time=end_time
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return new_shift
