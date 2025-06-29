from app.crud.stock_crud import save_stock_records
from app.database import SessionLocal
from app.models.models import Company
import cloudscraper
from datetime import datetime, timedelta
from io import StringIO
import pandas as pd


def save_init_stock_price(codes: list[str]) -> dict:
    scraper = cloudscraper.create_scraper()
    today = datetime.today()
    start_date = (today - timedelta(days=365 * 3)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")

    db = SessionLocal()
    success, fail = 0, 0

    for code in codes:
        company = db.query(Company).filter_by(isin_code=code).first()
        if not company:
            print(f"❌ ISIN Code {code}에 해당하는 회사 없음")
            fail += 1
            continue

        try:
            otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
            otp_payload = {
                'locale': 'ko_KR',
                "share": '1',
                "csvxls_isNo": 'false',
                "name": 'fileDown',
                "url": 'dbms/MDC/STAT/standard/MDCSTAT01701',
                'strtDd': start_date,
                'endDd': end_date,
                'adjStkPrc': 2,
                'adjStkPrc_check': 'Y',
                'isuCd': company.isin_code
            }
            otp_code = scraper.post(otp_url, data=otp_payload).text

            csv_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
            res = scraper.post(csv_url, data={'code': otp_code})
            res.encoding = 'EUC-KR'
            df = pd.read_csv(StringIO(res.text))

            save_stock_records(db, company, df)
            print(f"✅ 저장 완료: {company.company_name} ({code})")
            success += 1

        except Exception as e:
            print(f"❌ 오류 발생 ({code}): {e}")
            db.rollback()
            fail += 1

    db.close()
    print(f"\n📊 완료: 성공={success}, 실패={fail}")
    return {"success": success, "fail": fail}