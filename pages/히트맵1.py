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
# 화면
# ============================================================
st.title("🔥 월별 이용률 히트맵")

st.caption(
    "색이 진할수록 설비용량 대비 발전을 많이 한 달이에요."
)

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

start_month = st.sidebar.selectbox(
    "시작 월",
    month_list,
    index=0
)

end_month = st.sidebar.selectbox(
    "종료 월",
    month_list,
    index=len(month_list) - 1
)

if start_month > end_month:

    st.warning(
        "시작 월이 종료 월보다 늦을 수 없어요."
    )

    st.stop()

if len(selected) == 0:

    st.warning(
        "발전설비를 하나 이상 선택해 주세요."
    )

    st.stop()

start = pd.to_datetime(start_month + "-01")

end = (
    pd.to_datetime(end_month + "-01")
    + pd.offsets.MonthEnd(0)
)

filtered = df[
    (df[COL_FAC].isin(selected))
    &
    (df[COL_DATE] >= start)
    &
    (df[COL_DATE] <= end)
]

heat = filtered[
    filtered[COL_CAP] > 0
].copy()

if heat.empty:

    st.warning(
        "이용률을 계산할 수 있는 데이터가 없어요."
    )

    st.stop()

heat["월"] = (
    heat[COL_DATE]
    .dt.strftime("%Y-%m")
)

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

heat_table = heat_group.pivot(
    index=COL_FAC,
    columns="월",
    values="이용률"
)

fig = px.imshow(
    heat_table,
    aspect="auto",
    color_continuous_scale="YlGn",
    labels={
        "x": "월",
        "y": "발전설비",
        "color": "이용률(%)"
    }
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info(
    "💡 이용률 = 실제 발전량 ÷ (설비용량 × 24시간) × 100"
)
