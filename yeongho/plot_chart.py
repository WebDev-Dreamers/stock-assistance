import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib.ticker import MaxNLocator

# ✅ 폰트 및 스타일 설정
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
PLOT_STYLE = "seaborn-v0_8-muted"

if os.path.exists(FONT_PATH):
    font_name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    rc("font", family=font_name)

plt.style.use(PLOT_STYLE)

# ✅ 공통 차트 구성 설정
CHART_CONFIGS = [
    {
        "label": "1년 월간",
        "offset": pd.DateOffset(years=1),
        "group_fn": lambda d: d.dt.to_period("M").astype(str),
        "suffix": "monthly_1y",
        "xlabel": "월"
    },
    {
        "label": "3개월 주간",
        "offset": pd.DateOffset(months=3),
        "group_fn": lambda d: d.dt.to_period("W").astype(str),
        "suffix": "weekly_3m",
        "xlabel": "주"
    },
    {
        "label": "1개월 일간",
        "offset": pd.DateOffset(months=1),
        "group_fn": lambda d: d.dt.strftime("%Y-%m-%d"),
        "suffix": "daily_1m",
        "xlabel": "날짜"
    }
]


def save_line_chart(pivot_df, title, xlabel, legend_title, save_path):
    """📈 선형 차트를 저장합니다."""
    if pivot_df.empty:
        return False

    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    pivot_df.plot(ax=ax, marker='o', linewidth=2, markersize=5)

    ax.set_title(title, fontsize=15, weight="bold", pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("기사 수", fontsize=12)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xticks(range(len(pivot_df.index)))
    ax.set_xticklabels(pivot_df.index, rotation=45)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.legend(title=legend_title, bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return True


def generate_keyword_charts(data_path="yeongho/DATA", output_dir="yeongho/IMG", keywords_file="yeongho/config/keywords.json"):
    """🔍 키워드 기준 섹터별 기사 수 차트를 생성하고 저장합니다."""
    try:
        os.makedirs(output_dir, exist_ok=True)

        with open(keywords_file, encoding="utf-8") as f:
            keyword_mapping = json.load(f)

        df = pd.read_csv(os.path.join(data_path, "keyword.csv"))
        df["날짜"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
        today = pd.to_datetime("today")

        for sector, keywords in keyword_mapping.items():
            sector_df = df[(df["SECTOR"] == sector) & (df["KEYWORD"].isin(keywords))]

            for config in CHART_CONFIGS:
                filtered = sector_df[sector_df["날짜"] >= today - config["offset"]].copy()
                filtered["GROUP"] = config["group_fn"](filtered["날짜"])

                pivot_df = filtered.pivot_table(index="GROUP", columns="KEYWORD", values="CNT", aggfunc="sum").fillna(0)

                file_name = f"{sector}_{config['suffix']}.png"
                save_path = os.path.join(output_dir, file_name)

                if save_line_chart(
                    pivot_df=pivot_df,
                    title=f"{sector} - {config['label']} 키워드별 기사 수",
                    xlabel=config["xlabel"],
                    legend_title="키워드",
                    save_path=save_path
                ):
                    print(f"✅ 저장 완료: {file_name}")

    except Exception as e:
        print(f"❌ 키워드 차트 생성 실패: {e}")


def generate_sector_charts(data_path="yeongho/DATA", output_dir="yeongho/IMG"):
    """📊 전체 섹터별 기사 수 차트를 생성하고 저장합니다."""
    try:
        os.makedirs(output_dir, exist_ok=True)

        df = pd.read_csv(os.path.join(data_path, "sector.csv"))
        df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
        today = pd.to_datetime("today")

        for config in CHART_CONFIGS:
            filtered = df[df["DATE"] >= today - config["offset"]].copy()
            filtered["GROUP"] = config["group_fn"](filtered["DATE"])

            pivot_df = filtered.pivot_table(index="GROUP", columns="SECTOR", values="CNT", aggfunc="sum").fillna(0)
            file_name = f"sector_{config['suffix']}.png"
            save_path = os.path.join(output_dir, file_name)

            if save_line_chart(
                pivot_df=pivot_df,
                title=f"{config['label']} 섹터별 기사 수",
                xlabel=config["xlabel"],
                legend_title="섹터",
                save_path=save_path
            ):
                print(f"✅ 저장 완료: {file_name}")

    except Exception as e:
        print(f"❌ 섹터 차트 생성 실패: {e}")
