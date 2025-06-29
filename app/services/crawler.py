import os
import pandas as pd
import requests
import time
from io import StringIO
from concurrent.futures import ProcessPoolExecutor, as_completed

SAVE_DIR = "selected/selected_stocks"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_price_df(args):
    code, name, sector, max_pages = args
    dfs = []
    seen_dates = set()
    for page in range(1, max_pages + 1):
        url = f"https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = 'euc-kr'
        try:
            df = pd.read_html(StringIO(res.text), header=0)[0]
        except ValueError:
            break
        df = df.dropna()
        if df.empty: break
        if page_dates := set(df['날짜'].dropna()):
            if page_dates & seen_dates: break
            seen_dates.update(page_dates)
        df['code'], df['name'], df['codeSector'] = code, name, sector
        df = df[['날짜', 'codeSector', 'code', 'name', '종가', '시가', '고가', '저가', '거래량']]
        df.columns = ['date', 'codeSector', 'code', 'name', 'close', 'open', 'high', 'low', 'volume']
        df = df.sort_values('date')
        dfs.append(df)
        time.sleep(0.1)
    return pd.concat(dfs) if dfs else pd.DataFrame()

def fetch_stocks_from_db(db, max_pages=100):
    stocks = db.query(Stock).all()
    args_list = [(s.code, s.name, s.sector, max_pages) for s in stocks]
    results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_price_df, args) for args in args_list]
        for future in as_completed(futures):
            df = future.result()
            if not df.empty:
                results.append(df)
    if results:
        final = pd.concat(results, ignore_index=True)
        file_path = os.path.join(SAVE_DIR, "collected_prices.csv")
        final.to_csv(file_path, index=False, encoding="utf-8-sig")
        return file_path
    return None
