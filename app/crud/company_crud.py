from app.models.models import Company
from sqlalchemy.orm import Session
from app.database import SessionLocal


def set_liked_companies(names: list[str]) -> dict:
    db: Session = SessionLocal()
    success, fail = 0, 0

    for name in names:
        company = db.query(Company).filter_by(company_name=name).first()
        if company:
            company.is_liked = True
            db.add(company)
            success += 1
        else:
            fail += 1

    db.commit()
    db.close()
    return {"updated": success, "not_found": fail}