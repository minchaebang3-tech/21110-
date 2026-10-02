import csv
import glob
import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="신재생에너지 발전량 분석",
    page_icon="☀️",
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

    p {
        color: #4F6255;
    }

    hr {
        border: none;
        border-top: 1px solid #DCE8DC;
        margin: 1.5rem 0;
    }

    /* 버튼 */
    .stButton > button {
        width: 100%;
        min-height: 90px;
        border-radius: 18px;
        border: 1px solid #C9DEC9;
        background-color: white;
        color: #245C3A;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(45, 90, 55, 0.06);
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #78A96F;
        background-color: #EDF6E9;
        color: #245C3A;
        transform: translateY(-2px);
    }

    /* 안내 박스 */
    .info-box {
        background-color: #F0F7ED;
        border-left: 5px solid #76A86B;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #45604B;
        margin: 1rem 0;
    }

    /* 출처 박스 */
    .source-box {
        background-color: #FFF9E7;
        border: 1px solid #F0E2A9;
        border-radius: 12px;
        padding: 1rem;
        color: #6D623B;
        margin-top: 1.5rem;
    }

    /* 수치 카드 */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DCE8DC;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 3px 12px rgba(45, 90, 55, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #68786D;
    }

    [data-testid="stMetricValue"] {
        color: #245C3A;
        font-weight: 800;
    }

    /* 사이드바 */
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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        return main_path, False

    candidates = []

    for pattern in (
        "*.csv",
        "*.xlsx",
        "*.xls"
    ):
        candidates += glob.glob(
            os.path.join(
                BASE_DIR,
                pattern
            )
        )

    candidates = sorted(candidates)

    if candidates:
        return candidates[0], True

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
# 날짜 정리
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


# ============================================================
# 숫자 정리
# ============================================================
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


# ============================================================
# 데이터 불러오기
# ============================================================
try:

    data_path, used_other_file = find_data_file()

    df = load_data(data_path)

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
# 페이지 상태
# ============================================================
if "page" not in st.session_state:

    st.session_state.page = "home"


def go_home():

    st.session_state.page = "home"

    st.rerun()


def go_page(page):

    st.session_state.page = page

    st.rerun()


# ============================================================
# 지역 추정
# ============================================================
def get_region(facility):

    name = str(
        facility
    ).strip()

    if name.startswith("신보령"):
        return "보령"

    if name.startswith("신서천"):
        return "서천"

    if name.startswith("상명풍력"):
        return "제주"

    region_keywords = {

        "보령": "보령",
        "서울": "서울",
        "서천": "서천",
        "세종": "세종",
        "양양": "양양",
        "여수": "여수",
        "인천": "인천",
        "제주": "제주",
        "괴산": "괴산",
        "태안": "태안",
        "보성": "보성",
        "예천": "예천",

    }

    for keyword, region in region_keywords.items():

        if name.startswith(keyword):
            return region

    return "기타"


# ============================================================
# 메인 화면
# ============================================================
if st.session_state.page == "home":

    # 메인 상단 (HTML 태그 없이 streamlit 기본 기능으로만 만들어서
    # 태그 글자가 그대로 보일 걱정이 없어요)
    st.title("☀️ 신재생에너지 발전량 분석")
    st.caption("공공데이터로 살펴보는 우리의 친환경 에너지 생산")
    st.write("")

    # 요청한 문구
    st.subheader(
        "🌿 원하는 분석 선택!"
    )

    st.write(
        "원하는 분석을 선택하면 "
        "해당 데이터를 자세히 확인할 수 있습니다."
    )

    st.write("")

    # --------------------------------------------------------
    # 일별 / 월별
    # --------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📈  일별 발전량\n\n"
            "날짜별 발전량과 평균 이용률 확인",
            key="daily_button",
            use_container_width=True
        ):

            go_page("daily")

    with col2:

        if st.button(
            "📊  월별 발전량\n\n"
            "월별 발전량 변화 비교",
            key="monthly_button",
            use_container_width=True
        ):

            go_page("monthly")

    st.write("")

    # --------------------------------------------------------
    # 순위 / 지역
    # --------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:

        if st.button(
            "🏆  발전설비별 순위\n\n"
            "발전설비별 총 발전량 비교",
            key="ranking_button",
            use_container_width=True
        ):

            go_page("ranking")

    with col4:

        if st.button(
            "🗺️  지역별 발전량\n\n"
            "발전설비의 지역별 발전량 비교",
            key="region_button",
            use_container_width=True
        ):

            go_page("region")

    st.write("")

    # 데이터 기간
    st.markdown(
        f"""
        <div class="info-box">

            📅 <b>데이터 기간</b><br>

            {df[COL_DATE].min().strftime('%Y-%m-%d')}
            ~
            {df[COL_DATE].max().strftime('%Y-%m-%d')}

        </div>
        """,
        unsafe_allow_html=True
    )

    # 출처
    st.markdown(
        """
        <div class="source-box">

            ☀️ <b>데이터 출처</b><br>

            공공데이터포털(data.go.kr)
            한국중부발전(주) 신재생에너지 발전량

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 분석 페이지 공통
# ============================================================
if st.button(
    "← 🏠 메인으로 돌아가기",
    key="home_button"
):

    go_home()


st.divider()


# ============================================================
# 일별 발전량
# ============================================================
if st.session_state.page == "daily":

    st.title("📈 일별 발전량")

    st.caption(
        "날짜와 발전설비를 선택하여 "
        "일별 발전량을 확인하세요."
    )

    st.sidebar.header(
        "🌿 조건 선택"
    )

    facilities = sorted(
        df[COL_FAC].unique()
    )

    selected = st.sidebar.multiselect(
        "발전설비",
        facilities,
        default=facilities
    )

    min_date = (
        df[COL_DATE]
        .min()
        .date()
    )

    max_date = (
        df[COL_DATE]
        .max()
        .date()
    )

    period = st.sidebar.date_input(
        "기간",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )

    if (
        not isinstance(
            period,
            (tuple, list)
        )
        or len(period) != 2
    ):

        st.warning(
            "기간의 시작일과 종료일을 모두 선택해 주세요."
        )

        st.stop()

    if len(selected) == 0:

        st.warning(
            "발전설비를 하나 이상 선택해 주세요."
        )

        st.stop()

    start = pd.to_datetime(
        period[0]
    )

    end = pd.to_datetime(
        period[1]
    )

    filtered = df[
        (df[COL_FAC].isin(selected))
        &
        (df[COL_DATE] >= start)
        &
        (df[COL_DATE] <= end)
    ]

    if filtered.empty:

        st.warning(
            "선택한 조건에 해당하는 데이터가 없어요."
        )

        st.stop()

    total_gen = (
        filtered[COL_GEN]
        .sum()
    )

    num_days = (
        filtered[COL_DATE]
        .nunique()
    )

    daily_avg = (
        total_gen / num_days
        if num_days > 0
        else 0
    )

    valid = filtered[
        filtered[COL_CAP] > 0
    ]

    if len(valid) > 0:

        utilization = (
            valid[COL_GEN].sum()
            /
            (valid[COL_CAP] * 24).sum()
            * 100
        )

        util_text = (
            f"{utilization:.1f} %"
        )

    else:

        util_text = "계산 불가"

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "☀️ 총 발전량",
        f"{total_gen:,.0f} kWh"
    )

    c2.metric(
        "📅 일평균 발전량",
        f"{daily_avg:,.0f} kWh"
    )

    c3.metric(
        "🌿 평균 이용률",
        util_text
    )

    st.divider()

    daily = (
        filtered
        .groupby(
            [
                COL_DATE,
                COL_FAC
            ],
            as_index=False
        )[COL_GEN]
        .sum()
    )

    fig = px.line(
        daily,
        x=COL_DATE,
        y=COL_GEN,
        color=COL_FAC,
        labels={
            COL_DATE: "날짜",
            COL_GEN: "발전량(kWh)",
            COL_FAC: "발전설비"
        }
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "📋 데이터 표"
    )

    table = filtered.copy()

    table[COL_DATE] = (
        table[COL_DATE]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# 월별 발전량
# ============================================================
elif st.session_state.page == "monthly":

    st.title("📊 월별 발전량")

    st.caption(
        "월별 발전량의 변화를 한눈에 비교합니다."
    )

    st.sidebar.header(
        "🌿 조건 선택"
    )

    facilities = sorted(
        df[COL_FAC].unique()
    )

    selected = st.sidebar.multiselect(
        "발전설비",
        facilities,
        default=facilities
    )

    min_date = (
        df[COL_DATE]
        .min()
        .date()
    )

    max_date = (
        df[COL_DATE]
        .max()
        .date()
    )

    period = st.sidebar.date_input(
        "기간",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )

    if (
        not isinstance(
            period,
            (tuple, list)
        )
        or len(period) != 2
    ):

        st.warning(
            "기간의 시작일과 종료일을 모두 선택해 주세요."
        )

        st.stop()

    if len(selected) == 0:

        st.warning(
            "발전설비를 하나 이상 선택해 주세요."
        )

        st.stop()

    start = pd.to_datetime(
        period[0]
    )

    end = pd.to_datetime(
        period[1]
    )

    filtered = df[
        (df[COL_FAC].isin(selected))
        &
        (df[COL_DATE] >= start)
        &
        (df[COL_DATE] <= end)
    ]

    if filtered.empty:

        st.warning(
            "선택한 조건에 해당하는 데이터가 없어요."
        )

        st.stop()

    monthly = filtered.copy()

    monthly["월"] = (
        monthly[COL_DATE]
        .dt.strftime("%Y-%m")
    )

    monthly = (
        monthly
        .groupby(
            [
                "월",
                COL_FAC
            ],
            as_index=False
        )[COL_GEN]
        .sum()
    )

    fig = px.bar(
        monthly,
        x="월",
        y=COL_GEN,
        color=COL_FAC,
        labels={
            "월": "월",
            COL_GEN: "발전량(kWh)",
            COL_FAC: "발전설비"
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

    st.subheader(
        "📋 월별 발전량 표"
    )

    st.dataframe(
        monthly,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# 발전설비별 순위
# ============================================================
elif st.session_state.page == "ranking":

    st.title(
        "🏆 발전설비별 발전량 순위"
    )

    st.caption(
        "선택한 기간 동안 발전량이 많은 "
        "설비를 비교합니다."
    )

    min_date = (
        df[COL_DATE]
        .min()
        .date()
    )

    max_date = (
        df[COL_DATE]
        .max()
        .date()
    )

    period = st.date_input(
        "비교 기간",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )

    if (
        not isinstance(
            period,
            (tuple, list)
        )
        or len(period) != 2
    ):

        st.warning(
            "기간의 시작일과 종료일을 모두 선택해 주세요."
        )

        st.stop()

    start = pd.to_datetime(
        period[0]
    )

    end = pd.to_datetime(
        period[1]
    )

    ranking = df[
        (df[COL_DATE] >= start)
        &
        (df[COL_DATE] <= end)
    ].copy()

    facility_rank = (
        ranking
        .groupby(
            COL_FAC,
            as_index=False
        )[COL_GEN]
        .sum()
        .sort_values(
            COL_GEN,
            ascending=False
        )
    )

    max_n = min(
        20,
        len(facility_rank)
    )

    if max_n <= 1:
        top_n = max_n
    else:
        top_n = st.slider(
            "표시할 발전설비 수",
            min_value=1,
            max_value=max_n,
            value=min(10, max_n)
        )

    top_facilities = (
        facility_rank
        .head(top_n)
        .sort_values(
            COL_GEN
        )
    )

    fig = px.bar(
        top_facilities,
        x=COL_GEN,
        y=COL_FAC,
        orientation="h",
        labels={
            COL_GEN: "총 발전량(kWh)",
            COL_FAC: "발전설비"
        },
        title=f"발전량 상위 {top_n}개 설비"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "📋 전체 발전설비 순위"
    )

    ranking_table = (
        facility_rank.copy()
    )

    ranking_table.insert(
        0,
        "순위",
        range(
            1,
            len(ranking_table) + 1
        )
    )

    ranking_table = (
        ranking_table.rename(
            columns={
                COL_GEN:
                "총 발전량(kWh)"
            }
        )
    )

    st.dataframe(
        ranking_table,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# 지역별 발전량
# ============================================================
elif st.session_state.page == "region":

    st.title(
        "🗺️ 지역별 발전량"
    )

    st.caption(
        "발전설비 이름을 기준으로 지역을 "
        "추정하여 발전량을 비교합니다."
    )

    st.markdown(
        """
        <div class="info-box">

            💡 별도의 지역 컬럼이 없어
            발전설비 이름의 앞부분을 기준으로
            지역을 추정했습니다.

        </div>
        """,
        unsafe_allow_html=True
    )

    min_date = (
        df[COL_DATE]
        .min()
        .date()
    )

    max_date = (
        df[COL_DATE]
        .max()
        .date()
    )

    period = st.date_input(
        "비교 기간",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )

    if (
        not isinstance(
            period,
            (tuple, list)
        )
        or len(period) != 2
    ):

        st.warning(
            "기간의 시작일과 종료일을 모두 선택해 주세요."
        )

        st.stop()

    start = pd.to_datetime(
        period[0]
    )

    end = pd.to_datetime(
        period[1]
    )

    region_data = df[
        (df[COL_DATE] >= start)
        &
        (df[COL_DATE] <= end)
    ].copy()

    region_data["지역"] = (
        region_data[COL_FAC]
        .apply(get_region)
    )

    region_rank = (
        region_data
        .groupby(
            "지역",
            as_index=False
        )[COL_GEN]
        .sum()
        .sort_values(
            COL_GEN,
            ascending=False
        )
    )

    fig = px.bar(
        region_rank,
        x="지역",
        y=COL_GEN,
        labels={
            "지역": "추정 지역",
            COL_GEN: "총 발전량(kWh)"
        },
        title="지역별 총 발전량"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "📋 지역별 발전량"
    )

    region_table = (
        region_rank.copy()
    )

    region_table["발전량(MWh)"] = (
        region_table[COL_GEN] / 1000
    ).round(1)

    region_table = region_table[
        [
            "지역",
            "발전량(MWh)"
        ]
    ]

    st.dataframe(
        region_table,
        hide_index=True,
        use_container_width=True
    )
