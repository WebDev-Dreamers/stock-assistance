import pandas as pd
import requests
from io import StringIO
from app.database import SessionLocal
from app.models.models import Company, Sector


def fetch_krx_companies():
    url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

    res = requests.get(url)
    res.encoding = "euc-kr" 
  
    df = pd.read_html(StringIO(res.text), header=0)[0]
    df = df[['회사명', '종목코드', '업종', '주요제품']].dropna(subset=['업종'])
    df['종목코드'] = df['종목코드'].apply(lambda x: str(x).zfill(6))
    return df


def save_companies_to_db(df):
    db = SessionLocal()
    for _, row in df.iterrows():
        # 섹터가 이미 존재하는지 확인
        sector = db.query(Sector).filter_by(sector_name=row['업종']).first()
        if not sector:
            sector = Sector(sector_name=row['업종'])
            db.add(sector)
            db.commit()
            db.refresh(sector)

        # 회사 등록
        exists = db.query(Company).filter_by(company_code=row['종목코드']).first()
        if not exists:
            company = Company(
                company_name=row['회사명'],
                company_code=row['종목코드'],
                sector_id=sector.id,
                product_description=row['주요제품']
            )
            db.add(company)
    db.commit()
    db.close()


def main():
    df = fetch_krx_companies()
    save_companies_to_db(df)
    print(f"✅ 총 {len(df)}개 회사 저장 완료")


if __name__ == "__main__":
    main()