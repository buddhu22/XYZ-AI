from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.parent import ParentDetailResponse
from app.schemas.student import StudentDetailResponse
from app.services import parent_service

router = APIRouter()


@router.get("/{parent_id}", response_model=ParentDetailResponse, summary="Get parent profile by ID")
def get_parent_by_id(parent_id: int, db: Session = Depends(get_db)):
    """Retrieve parent details, user credentials (except password), and children info."""
    p = parent_service.get_parent_by_id(db, parent_id)
    return ParentDetailResponse(
        id=p.id,
        user_id=p.user_id,
        name=p.user.name,
        email=p.user.email,
        phone=p.phone,
        children=[
            StudentDetailResponse(
                id=s.id,
                roll_number=s.roll_number,
                class_name=s.class_name,
                section=s.section,
                user_id=s.user_id,
                name=s.user.name,
                email=s.user.email
            )
            for s in p.students
        ]
    )
