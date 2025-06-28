import requests
import pandas as pd


def get_isin_mapping() -> pd.DataFrame:
    url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
        "mktId": "ALL"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader"
    }

    res = requests.post(url, data=payload, headers=headers)
    
    try:
        data = res.json().get("OutBlock_1", [])
    except Exception as e:
        print("❌ JSON 파싱 실패:", e)
        print("응답 내용:", res.text[:500])  
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.rename(columns={
        "ISU_SRT_CD": "종목코드",
        "ISU_ABBRV": "종목명",
        "ISU_CD": "ISIN코드"
    })
    return df[["종목코드", "종목명", "ISIN코드"]]