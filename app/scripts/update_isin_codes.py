from app.database import SessionLocal
from app.models.models import Company
from app.scripts.isin_mapper import get_isin_mapping


def update_isin_codes():
    isin_df = get_isin_mapping()
    db = SessionLocal()

    updated = 0
    for _, row in isin_df.iterrows():
        company = db.query(Company).filter_by(company_code=row["종목코드"]).first()
        if company and not company.isin_code:
            company.isin_code = row["ISIN코드"]
            updated += 1

    db.commit()
    db.close()
    print(f"✅ ISIN 코드 {updated}개 회사에 업데이트 완료")


if __name__ == "__main__":
    update_isin_codes()