import os
import re
import json
import feedparser
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict  # 상단 import 추가

def load_keywords(filename="keywords.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "config", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_text(text: str) -> str:
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"[^\w\s]", "", text)  # 특수문자 제거
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_anchor_text(description: str) -> str:
    soup = BeautifulSoup(description, "html.parser")
    a_tag = soup.find("a")
    return a_tag.get_text(strip=True) if a_tag else description.strip()


def is_similar_description(new_desc, existing_descs, threshold=0.85):
    cleaned_new = clean_text(new_desc)
    cleaned_existing = [clean_text(d) for d in existing_descs]
    if not cleaned_existing:
        return False
    corpus = [cleaned_new] + cleaned_existing
    vectorizer = TfidfVectorizer().fit_transform(corpus)
    cos_sim = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    return (cos_sim > threshold).any()


def collect_google_news_by_keywords(keywords_dict, save_dir="yeongho/NewsData", max_workers=5):
    os.makedirs(save_dir, exist_ok=True)
    one_year_ago = datetime.today() - timedelta(days=365)

    results_by_date = {}
    saved_dates = set()
    total_fetched = 0

    total_keywords = sum(len(kw_list) for kw_list in keywords_dict.values())
    print(f"\n📡 뉴스 수집 시작: 총 {total_keywords} 키워드 / {max_workers} threads")

    def fetch_articles(sector, keyword):
        try:
            encoded = quote(keyword)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
            req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as res:
                feed_data = res.read()
            feed = feedparser.parse(feed_data)

            articles = []
            for entry in feed.entries:
                if not hasattr(entry, "published_parsed"):
                    continue
                pub_dt = datetime(*entry.published_parsed[:6])
                if pub_dt < one_year_ago:
                    continue
                date_str = pub_dt.strftime("%Y%m%d")
                display_date = pub_dt.strftime("%Y-%m-%d")

                description_text = extract_anchor_text(entry.description) if hasattr(entry, "description") else ""

                articles.append((
                    date_str,
                    {
                        "SECTOR": sector,
                        "KEYWORD": keyword,
                        "MEDIA": entry.source.title if hasattr(entry, "source") else "",
                        "TITLE": entry.title,
                        "DESCRIPTION": description_text,
                        "URL": entry.links[0].href,
                        "PUBLISHED": display_date,
                        "SCRAPED_AT": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                ))
            return (sector, keyword, len(articles), articles)
        except Exception as e:
            return (sector, keyword, -1, str(e))

    # 병렬 수집
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_articles, sector, keyword)
            for sector, keywords in keywords_dict.items()
            for keyword in keywords
        ]
        for future in as_completed(futures):
            sector, keyword, count, result = future.result()
            if count == -1:
                print(f"❌ [{sector}] '{keyword}' 수집 실패 → {result}")
            else:
                print(f"✅ [{sector}] '{keyword}' 완료 ({count}건)")
                total_fetched += count
                for date_str, article in result:
                    results_by_date.setdefault(date_str, []).append(article)


    # 날짜별 저장
    for date_str, articles in results_by_date.items():
        file_path = os.path.join(save_dir, f"{date_str}.csv")

        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            existing_urls = set(existing_df["URL"])
            existing_descs = defaultdict(set)
            for _, row in existing_df.iterrows():
                key = (row["SECTOR"], row["KEYWORD"])
                existing_descs[key].add(row["DESCRIPTION"])
        else:
            existing_df = pd.DataFrame()
            existing_urls = set()
            existing_descs = defaultdict(set)

        new_articles = []
        filtered_descriptions = []

        for a in articles:
            key = (a["SECTOR"], a["KEYWORD"])

            if a["URL"] in existing_urls or is_similar_description(a["DESCRIPTION"], existing_descs[key]):
                filtered_descriptions.append(a["DESCRIPTION"])
                continue

            new_articles.append(a)
            existing_descs[key].add(a["DESCRIPTION"])

        if new_articles:
            combined_df = pd.concat([existing_df, pd.DataFrame(new_articles)], ignore_index=True)
            combined_df.to_csv(file_path, index=False, encoding="utf-8-sig")
            saved_dates.add(date_str)

        # 로그 출력
        print(f"\n📅 {date_str} 요약")
        print(f" - 신규 기사 저장: {len(new_articles)}건")
        print(f" - 유사 기사 필터링: {len(filtered_descriptions)}건")
        for i, desc in enumerate(filtered_descriptions[:3], 1):
            print(f"   {i}. {desc}")
        if len(filtered_descriptions) > 3:
            print(f"   ...외 {len(filtered_descriptions) - 3}건 추가 필터링됨")


    print("\n📦 뉴스 수집 요약")
    print(f" - 총 수집 기사 수: {total_fetched}")
    print(f" - 저장된 날짜 수: {len(saved_dates)}")
    if saved_dates:
        print(f" - 저장된 CSV 파일 목록: {sorted(saved_dates)}.csv")
    else:
        print(" - 저장된 새 파일 없음 (모두 중복 또는 유사)")
