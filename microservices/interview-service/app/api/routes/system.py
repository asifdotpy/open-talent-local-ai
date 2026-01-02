from fastapi import APIRouter, Depends
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from app.api.deps import get_db
from app.db.models.system_version import SystemVersion

router = APIRouter()


@router.get("/db-status")
def db_status(session: Session = Depends(get_db)):
    try:
        # Check if we're using SQLModel's Session (has exec) or SQLAlchemy's Session (has execute)
        if hasattr(session, "exec"):
            version = session.exec(select(SystemVersion)).first()
        else:
            version = session.execute(select(SystemVersion)).scalar_one_or_none()
        return {
            "db_status": "ok",
            "system_version": version.version if version else None,
            "detail": "No error",
        }
    except OperationalError as e:
        return {"db_status": "error", "detail": str(e)}
    except Exception as e:
        return {"db_status": "error", "detail": str(e)}


# Health check endpoint
@router.get("/health")
def health_status():
    return {"status": "healthy"}
