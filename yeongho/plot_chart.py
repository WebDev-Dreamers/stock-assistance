import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib.ticker import MaxNLocator
import matplotlib as mpl
import seaborn as sns

# ✅ 폰트 설정
import matplotlib as mpl

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"  # 윈도우용 맑은 고딕
if os.path.exists(FONT_PATH):
    font_name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    mpl.rcParams["font.family"] = font_name
else:
    # 대체용 (macOS/Linux 등)
    mpl.rcParams["font.family"] = "AppleGothic"  # mac
    # mpl.rcParams["font.family"] = "NanumGothic"  # Linux용 설치 시

# ✅ 마이너한 깨짐 방지
mpl.rcParams['axes.unicode_minus'] = False

plt.style.use("seaborn-v0_8-muted")

# ✅ 공통 차트 구성 설정 (기존 코드 유지)
CHART_CONFIGS = [
    {"label": "1년 월간", "offset": pd.DateOffset(years=1), "group_fn": lambda d: d.dt.to_period("M").astype(str), "suffix": "monthly_1y", "xlabel": "월"},
    {"label": "3개월 주간", "offset": pd.DateOffset(months=3), "group_fn": lambda d: d.dt.to_period("W").astype(str), "suffix": "weekly_3m", "xlabel": "주"},
    {"label": "1개월 일간", "offset": pd.DateOffset(months=1), "group_fn": lambda d: d.dt.strftime("%Y-%m-%d"), "suffix": "daily_1m", "xlabel": "날짜"}
]
def save_line_chart(pivot_df, title, xlabel, legend_title, save_path):
    if pivot_df.empty:
        return False

    fig, ax = plt.subplots(figsize=(14, 7), dpi=120)

    num_series = len(pivot_df.columns)
    if num_series <= 10:
        palette = sns.color_palette("Set2", n_colors=num_series)
    elif num_series <= 20:
        palette = sns.color_palette("tab20", n_colors=num_series)
    else:
        palette = sns.color_palette("husl", n_colors=num_series)
    color_map = dict(zip(pivot_df.columns, palette))

    # ✅ 마커 스타일 목록 (색상과 함께 구분용)
    marker_styles = ['o', 's', '^', 'D', 'P', '*', 'X', 'v', '<', '>']

    for i, col in enumerate(pivot_df.columns):
        marker = marker_styles[i % len(marker_styles)]

        ax.plot(
            pivot_df.index,
            pivot_df[col],
            label=col,
            marker=marker,
            linestyle='-',  # ✅ 실선으로 통일
            linewidth=2.5,
            markersize=6,
            color=color_map[col],
            zorder=3
        )

        # ✅ 끝점 라벨
        if not pivot_df[col].isnull().all():
            last_valid_idx = pivot_df[col].last_valid_index()
            if last_valid_idx is not None:
                x_val = pivot_df.index.get_loc(last_valid_idx)
                y_val = pivot_df[col].loc[last_valid_idx]
                ax.text(
                    x=x_val + 0.1,
                    y=y_val,
                    s=f" {col}",
                    fontsize=9,
                    color=color_map[col],
                    verticalalignment='center',
                    horizontalalignment='left',
                    zorder=5,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
                )

    ax.set_title(title, fontsize=18, fontweight="bold", pad=25, color='#333333')
    ax.set_xlabel(xlabel, fontsize=14, labelpad=15, color='#555555')
    ax.set_ylabel("기사 수", fontsize=14, labelpad=15, color='#555555')
    ax.grid(True, linestyle=':', linewidth=0.6, alpha=0.5, color='#aaaaaa')
    ax.set_xticks(range(len(pivot_df.index)))
    ax.set_xticklabels(pivot_df.index, rotation=45, ha='right', fontsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='y', labelsize=9)

    if num_series <= 20:
        ax.legend(title=legend_title, bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9, frameon=False)

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    return True



def generate_sector_charts(data_path="yeongho/DATA", output_dir="yeongho/IMG/sector"):
    """📊 일반 섹터별 기사 수 합계 차트 생성"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_csv(os.path.join(data_path, "sector.csv"))
        df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
        today = pd.to_datetime("today")

        sectors = [s for s in df["SECTOR"].unique() if "_이슈" not in s and "_팀" not in s]

        for sector in sectors:
            sector_df = df[df["SECTOR"] == sector]
            for config in CHART_CONFIGS:
                filtered = sector_df[sector_df["DATE"] >= today - config["offset"]].copy()
                filtered["GROUP"] = config["group_fn"](filtered["DATE"])
                pivot_df = filtered.groupby("GROUP")["CNT"].sum().reset_index().set_index("GROUP")

                chart_title = f"{sector} - {config['label']} 기사 수 추이"
                file_name = f"{sector}_{config['suffix']}.png"
                save_path = os.path.join(output_dir, file_name)

                if save_line_chart(pivot_df, chart_title, config["xlabel"], "기사 수", save_path):
                    print(f"✅ 저장 완료: {save_path}")
    except Exception as e:
        print(f"❌ 섹터 차트 생성 실패: {e}")





def generate_keyword_charts(data_path="yeongho/DATA", output_dir="yeongho/IMG/keyword", keywords_file="yeongho/config/keywords.json"):
    """🔍 섹터별 키워드 기사 수 비교 차트"""
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

                file_name = f"{sector}_keyword_{config['suffix']}.png"
                save_path = os.path.join(output_dir, file_name)

                if save_line_chart(pivot_df, f"{sector} - {config['label']} 키워드별 기사 수", config["xlabel"], "키워드", save_path):
                    print(f"✅ 저장 완료: {save_path}")
    except Exception as e:
        print(f"❌ 키워드 차트 생성 실패: {e}")



def generate_issue_charts(data_path="yeongho/DATA", output_dir="yeongho/IMG/issue"):
    """🧩 이슈 섹터별 '총 기사 수' 추이 선그래프 생성"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_csv(os.path.join(data_path, "sector.csv"))
        df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
        today = pd.to_datetime("today")

        issue_sectors = [s for s in df["SECTOR"].unique() if "_이슈" in s]

        for sector in issue_sectors:
            sector_df = df[df["SECTOR"] == sector]

            for config in CHART_CONFIGS:
                filtered = sector_df[sector_df["DATE"] >= today - config["offset"]].copy()
                filtered["GROUP"] = config["group_fn"](filtered["DATE"])
                pivot_df = (
                    filtered.groupby("GROUP")["CNT"]
                    .sum()
                    .reset_index()
                    .set_index("GROUP")
                )

                chart_title = f"{sector.replace('_이슈','')} - {config['label']} 이슈 기사 수 추이"
                file_name = f"{sector}_{config['suffix']}.png"
                save_path = os.path.join(output_dir, file_name)

                if save_line_chart(pivot_df, chart_title, config["xlabel"], "기사 수", save_path):
                    print(f"✅ 저장 완료: {save_path}")

    except Exception as e:
        print(f"❌ 이슈 차트 생성 실패: {e}")

