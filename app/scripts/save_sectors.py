import pandas as pd
import requests
from app.database import SessionLocal
from app.models.models import Sector


def fetch_krx_sectors():
    url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

    res = requests.get(url)
    res.encoding = "euc-kr" 
  
    df = pd.read_html(res.text, header=0)[0]
    sector_names = df['업종'].dropna().unique().tolist()
    return sector_names


def save_sectors_to_db(sector_names):
    db = SessionLocal()
    for name in sector_names:
        exists = db.query(Sector).filter_by(name=name).first()
        if not exists:
            db.add(Sector(name=name))
    db.commit()
    db.close()


def main():
    sector_names = fetch_krx_sectors()
    save_sectors_to_db(sector_names)
    print(f"✅ 총 {len(sector_names)}개 업종 저장 완료")


if __name__ == "__main__":
    main()
