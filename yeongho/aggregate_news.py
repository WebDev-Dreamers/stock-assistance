import os
import pandas as pd
from collections import defaultdict


def aggregate_news_counts(news_dir="yeongho/NewsData", output_dir="yeongho/DATA"):
    """
    📊 날짜별 뉴스 기사 데이터를 집계하여 키워드 및 섹터 기준 CSV로 저장합니다.
    
    - 입력: news_dir 안에 존재하는 YYYYMMDD.csv 형태의 파일들
    - 출력: output_dir에 keyword.csv, sector.csv 저장
    """
    keyword_stats = []  # (DATE, SECTOR, KEYWORD, CNT)
    sector_stats = []   # (DATE, SECTOR, CNT)

    try:
        csv_files = sorted(f for f in os.listdir(news_dir) if f.endswith(".csv"))
        if not csv_files:
            print("⚠️ 뉴스 CSV 파일이 없습니다.")
            return

        for filename in csv_files:
            file_path = os.path.join(news_dir, filename)
            date_str = filename.replace(".csv", "")

            try:
                df = pd.read_csv(file_path)

                keyword_counts = defaultdict(int)
                sector_counts = defaultdict(int)

                for _, row in df.iterrows():
                    keyword_counts[(row["SECTOR"], row["KEYWORD"])] += 1
                    sector_counts[row["SECTOR"]] += 1

                keyword_stats.extend(
                    (date_str, sector, keyword, count)
                    for (sector, keyword), count in keyword_counts.items()
                )
                sector_stats.extend(
                    (date_str, sector, count)
                    for sector, count in sector_counts.items()
                )

            except Exception as file_error:
                print(f"❌ 파일 처리 실패: {filename} | {file_error}")

        os.makedirs(output_dir, exist_ok=True)

        keyword_df = pd.DataFrame(keyword_stats, columns=["DATE", "SECTOR", "KEYWORD", "CNT"])
        sector_df = pd.DataFrame(sector_stats, columns=["DATE", "SECTOR", "CNT"])

        keyword_path = os.path.join(output_dir, "keyword.csv")
        sector_path = os.path.join(output_dir, "sector.csv")

        keyword_df.to_csv(keyword_path, index=False, encoding="utf-8-sig")
        sector_df.to_csv(sector_path, index=False, encoding="utf-8-sig")

        print(f"✅ 집계 완료 및 저장됨:\n - {keyword_path}\n - {sector_path}")

    except Exception as dir_error:
        print(f"❌ 디렉토리 접근 실패: {dir_error}")
