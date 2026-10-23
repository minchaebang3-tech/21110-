import csv
import glob
import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 페이지 기본 설정
# ============================================================
st.set_page_config(
    page_title="이용률 히트맵",
    page_icon="🔥",
    layout="wide"
)


# ============================================================
# 디자인
# ============================================================
st.markdown("""
<style>

    .stApp {
        background-color: #F7FAF5;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    h1 {
        color: #245C3A;
        font-weight: 800;
    }

    h2, h3 {
        color: #2F6B45;
    }

    [data-testid="stSidebar"] {
        background-color: #EFF6EC;
        border-right: 1px solid #DCE8DC;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #245C3A;
    }

</style>
""", unsafe_allow_html=True)


# pages 폴더 안이므로 한 칸 위(메인 파일이 있는 곳)에서 data.csv를 찾음
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

COL_DATE = "연월일"
COL_FAC = "발전설비"
COL_CAP = "설비용량(kW)"
COL_GEN = "발전량(kWh)"


class DataError(Exception):
    pass


# ============================================================
# 데이터 파일 찾기
# ============================================================
def find_data_file():

    main_path = os.path.join(
        BASE_DIR,
        "data.csv"
    )

    if os.path.exists(main_path):
        return main_path

    candidates = []

    for pattern in (
        "*.csv",
        "*.xlsx",
        "*.xls"
    ):
        candidates += glob.glob(
            os.path.join(BASE_DIR, pattern)
        )

    candidates = sorted(candidates)

    if candidates:
        return candidates[0]

    raise FileNotFoundError("data.csv")


# ============================================================
# CSV / 엑셀 읽기
# ============================================================
def find_header_index(rows):

    for i, row in enumerate(rows[:100]):

        cells = [
            str(c).strip()
            for c in row
        ]

        has_date = any(
            c.startswith("연월일")
            for c in cells
        )

        has_gen = any(
            c.startswith("발전량")
            for c in cells
        )

        if has_date and has_gen:
            return i

    return None


def rows_to_df(rows, header_idx):

    header = [
        str(c).strip()
        for c in rows[header_idx]
    ]

    n = len(header)

    body = []

    for r in rows[header_idx + 1:]:

        r = list(r)

        r = (
            r
            + [""] * n
        )[:n]

        body.append(r)

    return pd.DataFrame(
        body,
        columns=header
    )


def read_table(path):

    with open(path, "rb") as f:
        head = f.read(8)

    # 엑셀
    if (
        head[:2] == b"PK"
        or head[:4] == b"\xd0\xcf\x11\xe0"
    ):

        engine = (
            "openpyxl"
            if head[:2] == b"PK"
            else "xlrd"
        )

        raw = pd.read_excel(
            path,
            header=None,
            engine=engine
        )

        raw = raw.astype(object).where(
            raw.notna(),
            ""
        )

        rows = raw.values.tolist()

        idx = find_header_index(rows)

        if idx is None:

            raise DataError(
                "엑셀 파일에서 제목줄을 찾지 못했어요."
            )

        return rows_to_df(
            rows,
            idx
        )

    # CSV
    with open(path, "rb") as f:
        data = f.read()

    for enc in (
        "utf-8-sig",
        "cp949",
        "utf-16"
    ):

        try:
            text = data.decode(enc)

        except UnicodeDecodeError:
            continue

        for sep in (
            ",",
            "\t",
            ";",
            "|"
        ):

            try:

                rows = list(
                    csv.reader(
                        io.StringIO(text),
                        delimiter=sep
                    )
                )

            except Exception:
                continue

            idx = find_header_index(rows)

            if idx is not None:

                return rows_to_df(
                    rows,
                    idx
                )

    raise DataError(
        "파일에서 제목줄을 찾지 못했어요."
    )


# ============================================================
# 날짜 / 숫자 정리
# ============================================================
def parse_dates(series):

    if pd.api.types.is_datetime64_any_dtype(series):
        return series

    t = (
        series
        .astype(str)
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True
        )
    )

    parsed = pd.to_datetime(
        t,
        format="%Y%m%d",
        errors="coerce"
    )

    num = pd.to_numeric(
        t,
        errors="coerce"
    )

    serial = pd.to_datetime(
        num.where(
            num.between(
                20000,
                80000
            )
        ),
        unit="D",
        origin="1899-12-30"
    )

    parsed = parsed.fillna(serial)

    if parsed.isna().any():

        auto = pd.to_datetime(
            t.where(
                parsed.isna()
            ),
            errors="coerce"
        )

        parsed = parsed.fillna(auto)

    return parsed


def to_number(series):

    cleaned = (
        series
        .astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.strip()
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    )


# ============================================================
# 데이터 불러오기
# ============================================================
@st.cache_data
def load_data(path):

    df = read_table(path)

    rename = {}

    for c in df.columns:

        name = str(c).strip()

        if name.startswith("연월일"):
            rename[c] = COL_DATE

        elif name.startswith("발전설비"):
            rename[c] = COL_FAC

        elif name.startswith("설비용량"):
            rename[c] = COL_CAP

        elif name.startswith("발전량"):
            rename[c] = COL_GEN

    df = df.rename(
        columns=rename
    )

    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    missing = [
        c
        for c in (
            COL_DATE,
            COL_FAC,
            COL_CAP,
            COL_GEN
        )
        if c not in df.columns
    ]

    if missing:

        raise DataError(
            "필요한 컬럼이 없어요: "
            + ", ".join(missing)
        )

    df = df[
        [
            COL_DATE,
            COL_FAC,
            COL_CAP,
            COL_GEN
        ]
    ].copy()

    df[COL_DATE] = parse_dates(
        df[COL_DATE]
    )

    df[COL_CAP] = to_number(
        df[COL_CAP]
    )

    df[COL_GEN] = to_number(
        df[COL_GEN]
    )

    df[COL_FAC] = (
        df[COL_FAC]
        .astype(str)
        .str.strip()
    )

    df = df.dropna(
        subset=[
            COL_DATE,
            COL_GEN
        ]
    )

    df = df[
        ~df[COL_FAC].isin(
            [
                "",
                "nan",
                "None"
            ]
        )
    ]

    if df.empty:

        raise DataError(
            "정리하고 나니 남은 데이터가 없어요."
        )

    return (
        df
        .sort_values(COL_DATE)
        .reset_index(drop=True)
    )


try:

    df = load_data(find_data_file())

except FileNotFoundError:

    st.error(
        "데이터 파일을 찾을 수 없어요. "
        "GitHub에 data.csv가 있는지 확인해 주세요."
    )

    st.stop()

except DataError as e:

    st.error(
        f"데이터 파일 문제: {e}"
    )

    st.stop()

except Exception as e:

    st.error(
        f"데이터를 읽는 중 문제가 생겼어요: "
        f"{type(e).__name__}: {e}"
    )

    st.stop()


# ============================================================
# 화면 제목
# ============================================================
st.title("🔥 월별 이용률 히트맵")

st.caption(
    "이용률 = 실제 발전량 ÷ (설비용량 × 24시간) × 100  |  "
    "색이 진할수록 이용률이 높고, 빈칸은 데이터가 없는 달이에요."
)


# ============================================================
# 사이드바 조건
# ============================================================
st.sidebar.header("🌿 조건 선택")

facilities = sorted(
    df[COL_FAC].unique()
)

selected = st.sidebar.multiselect(
    "발전설비",
    facilities,
    default=facilities
)

month_list = sorted(
    df[COL_DATE].dt.strftime("%Y-%m").unique()
)


def month_label(m):

    return f"{m[:4]}년 {int(m[5:])}월"


# 기본값은 가장 최근 6개월
selected_months = st.sidebar.multiselect(
    "월 선택",
    month_list,
    default=month_list[-6:],
    format_func=month_label
)

if len(selected_months) == 0:

    st.warning(
        "월을 하나 이상 선택해 주세요."
    )

    st.stop()

if len(selected) == 0:

    st.warning(
        "발전설비를 하나 이상 선택해 주세요."
    )

    st.stop()


# ============================================================
# 이용률 계산
# ============================================================
data = df.copy()

data["월"] = (
    data[COL_DATE]
    .dt.strftime("%Y-%m")
)

heat = data[
    (data[COL_FAC].isin(selected))
    &
    (data["월"].isin(selected_months))
    &
    (data[COL_CAP] > 0)
].copy()

if heat.empty:

    st.warning(
        "이용률을 계산할 수 있는 데이터가 없어요."
    )

    st.stop()

heat["가능발전량"] = heat[COL_CAP] * 24

heat_group = (
    heat
    .groupby(
        ["월", COL_FAC],
        as_index=False
    )[[COL_GEN, "가능발전량"]]
    .sum()
)

heat_group["이용률"] = (
    heat_group[COL_GEN]
    / heat_group["가능발전량"]
    * 100
)


# ============================================================
# 이상값 설비 찾기 (이용률 100% 초과)
# → 지우지 않고 표시만 한다
# ============================================================
over_set = set(
    heat_group[
        heat_group["이용률"] > 100
    ][COL_FAC]
)


# ============================================================
# 표 만들기
# ============================================================
heat_table = heat_group.pivot(
    index=COL_FAC,
    columns="월",
    values="이용률"
)

# 선택한 월만 시간 순서대로
heat_table = heat_table[
    sorted(heat_table.columns)
]

# 데이터가 아예 없는 설비 줄 제거
heat_table = heat_table.dropna(how="all")

# 평균 이용률이 높은 설비가 위로
avg = heat_table.mean(axis=1)

heat_table = heat_table.loc[
    avg.sort_values(ascending=False).index
]

# 이상값 설비는 이름 앞에 ⚠️ 표시
heat_table.index = [
    f"⚠️ {name}" if name in over_set else name
    for name in heat_table.index
]

# 월 이름을 한글로
heat_table.columns = [
    month_label(m)
    for m in heat_table.columns
]


# ============================================================
# 히트맵 결과 요약 (3줄) - 선택한 데이터에 맞게 자동으로 바뀜
# → 이상값 설비는 빼고 계산
# ============================================================
def get_type(name):

    if "ESS" in name:
        return None

    for key in (
        "연료전지",
        "태양광",
        "풍력",
        "수력"
    ):

        if key in name:
            return key

    return None


normal_group = heat_group[
    ~heat_group[COL_FAC].isin(over_set)
]

summary_lines = []

if len(normal_group) > 0:

    # 1줄: 설비별 최고 / 최저
    fac_avg = (
        normal_group
        .groupby(COL_FAC)["이용률"]
        .mean()
    )

    summary_lines.append(
        f"이용률이 가장 높은 설비는 {fac_avg.idxmax()}"
        f"({fac_avg.max():.1f}%), "
        f"가장 낮은 설비는 {fac_avg.idxmin()}"
        f"({fac_avg.min():.1f}%)예요."
    )

    # 2줄: 월별 최고 / 최저
    month_avg = (
        normal_group
        .groupby("월")["이용률"]
        .mean()
    )

    if len(month_avg) >= 2:

        summary_lines.append(
            f"전체 평균 이용률은 {month_label(month_avg.idxmax())}에 "
            f"가장 높고({month_avg.max():.1f}%), "
            f"{month_label(month_avg.idxmin())}에 "
            f"가장 낮아요({month_avg.min():.1f}%)."
        )

    else:

        summary_lines.append(
            "월을 두 개 이상 선택하면 달마다 이용률이 "
            "어떻게 변하는지 비교할 수 있어요."
        )

    # 3줄: 발전 유형별 평균
    type_df = pd.DataFrame(
        {
            "avg": fac_avg,
            "type": pd.Series(
                {
                    n: get_type(n)
                    for n in fac_avg.index
                }
            )
        }
    ).dropna(subset=["type"])

    if len(type_df) > 0:

        type_avg = (
            type_df
            .groupby("type")["avg"]
            .mean()
            .sort_values(ascending=False)
        )

        summary_lines.append(
            "유형별 평균 이용률은 "
            + " > ".join(
                f"{t} {v:.1f}%"
                for t, v in type_avg.items()
            )
            + "예요."
        )

else:

    summary_lines.append(
        "정상 범위의 이용률 데이터가 없어 요약을 만들 수 없어요."
    )

st.info(
    "📊 **히트맵 결과 요약**  \n"
    + "  \n".join(summary_lines)
)

if len(over_set) > 0:

    st.warning(
        "⚠️ 표시된 설비는 이용률이 100%를 넘는 달이 있어요. "
        "원본 데이터의 설비용량을 확인해 보세요."
    )


# ============================================================
# 히트맵 (결과 요약을 그래프 제목에 넣어서 이미지 저장 시 같이 저장)
# ============================================================
fig = px.imshow(
    heat_table,
    aspect="auto",
    color_continuous_scale="YlGn",
    zmin=0,
    zmax=100,
    text_auto=".0f",
    labels={
        "x": "월",
        "y": "발전설비",
        "color": "이용률(%)"
    }
)

# 월을 날짜가 아니라 칸(항목)으로 취급
fig.update_xaxes(
    type="category"
)

title_text = (
    "<b>월별 발전설비 이용률 히트맵</b><br>"
    + "<br>".join(summary_lines)
)

fig.update_layout(
    title=dict(
        text=title_text,
        x=0,
        xanchor="left",
        font=dict(size=13, color="#2F4F3A")
    ),
    margin=dict(t=160),
    plot_bgcolor="white",
    paper_bgcolor="white",
    dragmode="zoom",
    height=max(
        550,
        30 * len(heat_table) + 220
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "이용률_히트맵",
            "scale": 2
        }
    }
)

st.caption(
    "💾 그래프 오른쪽 위 카메라 아이콘을 누르면 "
    "결과 요약이 포함된 이미지로 저장돼요."
)


# ============================================================
# 이상값 설비 확인표
# ============================================================
if len(over_set) > 0:

    with st.expander("🔍 이용률 100% 초과 설비 확인하기"):

        check = (
            heat[
                heat[COL_FAC].isin(over_set)
            ]
            .groupby(COL_FAC)
            .agg(
                설비용량=(COL_CAP, "max"),
                일평균발전량=(COL_GEN, "mean")
            )
            .reset_index()
        )

        check["이용률(%)"] = (
            check["일평균발전량"]
            / (check["설비용량"] * 24)
            * 100
        ).round(1)

        check = check.rename(
            columns={
                "설비용량": "설비용량(kW)",
                "일평균발전량": "일평균 발전량(kWh)"
            }
        )

        check["일평균 발전량(kWh)"] = (
            check["일평균 발전량(kWh)"].round(1)
        )

        st.write(
            "설비용량(kW)이 실제 발전량에 비해 너무 작게 적혀 있으면 "
            "이용률이 100%를 넘게 나와요."
        )

        st.dataframe(
            check,
            hide_index=True,
            use_container_width=True
        )
