from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.parent import Parent


def get_parent_by_id(db: Session, parent_id: int) -> Parent:
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    return parent
