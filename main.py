import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 페이지 설정
# ------------------------------------------------------------
st.set_page_config(page_title="재생에너지 발전량 대시보드", layout="wide")
st.title("☀️ 한국중부발전 신재생에너지 발전량 대시보드")
st.caption("출처: 공공데이터포털(data.go.kr) 한국중부발전 신재생에너지 발전량 (일별)")

# 필요한 컬럼 이름 (CSV의 컬럼명과 같아야 해요)
COL_DATE = "연월일"
COL_FAC = "발전설비"
COL_CAP = "설비용량(kW)"
COL_GEN = "발전량(kWh)"


# ------------------------------------------------------------
# 1. 데이터 불러오기 (한 번 읽으면 저장해두는 캐시 사용)
# ------------------------------------------------------------
@st.cache_data
def load_data(path):
    # 파일 맨 앞 글자로 진짜 엑셀 파일인지 확인 (엑셀은 "PK"로 시작해요)
    with open(path, "rb") as f:
        head = f.read(2)

    if head == b"PK":
        # 엑셀(.xlsx)을 data.csv로 이름만 바꾼 경우
        df = pd.read_excel(path)
    else:
        # 인코딩: utf-8-sig로 먼저 읽고, 실패하면 cp949로 읽기
        # sep=None: 쉼표/탭 등 구분 기호를 자동으로 찾아요
        df = None
        for enc in ["utf-8-sig", "cp949"]:
            try:
                df = pd.read_csv(path, encoding=enc, sep=None, engine="python")
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        if df is None:
            raise ValueError("CSV 인코딩이나 형식을 읽을 수 없어요.")

    # 컬럼 이름 정리 (단위가 있든 없든 같은 이름으로 통일)
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
    df = df.rename(columns=rename)

    # 필요한 컬럼이 다 있는지 확인
    for col in [COL_DATE, COL_FAC, COL_CAP, COL_GEN]:
        if col not in df.columns:
            raise KeyError(col)

    # 연월일 -> 날짜 형식 (20231101 같은 숫자 형태도 처리)
    if not pd.api.types.is_datetime64_any_dtype(df[COL_DATE]):
        s = df[COL_DATE].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        parsed = pd.to_datetime(s, format="%Y%m%d", errors="coerce")
        if parsed.isna().mean() > 0.5:
            parsed = pd.to_datetime(s, errors="coerce")
        df[COL_DATE] = parsed

    # 숫자 컬럼 -> 숫자 형식 (쉼표가 있어도 처리)
    for col in [COL_CAP, COL_GEN]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )

    # 발전설비 이름 앞뒤 공백 제거
    df[COL_FAC] = df[COL_FAC].astype(str).str.strip()

    # 날짜나 발전량이 비어 있는 행은 제거
    df = df.dropna(subset=[COL_DATE, COL_GEN])
    return df


try:
    df = load_data("data.csv")
except FileNotFoundError:
    st.error("data.csv 파일을 찾을 수 없어요. GitHub 저장소에 data.csv를 올렸는지 확인해 주세요.")
    st.stop()
except KeyError as e:
    st.error(f"CSV에 '{e.args[0]}' 컬럼이 없어요. 컬럼 이름을 확인해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 읽는 중 문제가 생겼어요: {e}")
    st.stop()

if df.empty:
    st.error("데이터가 비어 있어요. CSV 파일 내용을 확인해 주세요.")
    st.stop()


# ------------------------------------------------------------
# 2. 사이드바: 발전설비 선택 + 기간 선택
# ------------------------------------------------------------
st.sidebar.header("🔎 조건 선택")

# 발전설비 다중 선택 (기본값: 전부 선택)
facilities = sorted(df[COL_FAC].unique())
selected = st.sidebar.multiselect("발전설비", facilities, default=facilities)

# 기간 선택 (기본값: 전체 기간)
min_date = df[COL_DATE].min().date()
max_date = df[COL_DATE].max().date()
period = st.sidebar.date_input(
    "기간",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# 시작일/종료일 둘 다 골랐는지 확인
if not isinstance(period, (tuple, list)) or len(period) != 2:
    st.warning("기간의 시작일과 종료일을 모두 선택해 주세요.")
    st.stop()

if len(selected) == 0:
    st.warning("발전설비를 하나 이상 선택해 주세요.")
    st.stop()

start, end = pd.to_datetime(period[0]), pd.to_datetime(period[1])

# 선택한 조건으로 데이터 걸러내기
filtered = df[
    (df[COL_FAC].isin(selected))
    & (df[COL_DATE] >= start)
    & (df[COL_DATE] <= end)
]

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없어요. 조건을 바꿔 보세요.")
    st.stop()


# ------------------------------------------------------------
# 3. 카드 3개: 총 발전량 / 일평균 발전량 / 평균 이용률
# ------------------------------------------------------------
total_gen = filtered[COL_GEN].sum()

# 일평균 = 총 발전량 ÷ 날짜 수
num_days = filtered[COL_DATE].nunique()
daily_avg = total_gen / num_days

# 이용률 = 발전량 ÷ (설비용량 × 24시간)
# 설비용량이 0이거나 비어 있는 행은 계산에서 제외
valid = filtered[filtered[COL_CAP] > 0]
if len(valid) > 0:
    utilization = valid[COL_GEN].sum() / (valid[COL_CAP] * 24).sum() * 100
    util_text = f"{utilization:.1f} %"
else:
    util_text = "계산 불가"

c1, c2, c3 = st.columns(3)
c1.metric("총 발전량", f"{total_gen:,.0f} kWh")
c2.metric("일평균 발전량", f"{daily_avg:,.0f} kWh")
c3.metric("평균 이용률", util_text)

st.divider()


# ------------------------------------------------------------
# 4. 일별 발전량 선 그래프
# ------------------------------------------------------------
st.subheader("📈 일별 발전량")
daily = filtered.groupby([COL_DATE, COL_FAC], as_index=False)[COL_GEN].sum()
fig_line = px.line(
    daily,
    x=COL_DATE,
    y=COL_GEN,
    color=COL_FAC,
    labels={COL_DATE: "날짜", COL_GEN: "발전량(kWh)", COL_FAC: "발전설비"},
)
st.plotly_chart(fig_line, use_container_width=True)


# ------------------------------------------------------------
# 5. 월별 총 발전량 막대 그래프
# ------------------------------------------------------------
st.subheader("📊 월별 총 발전량")
monthly = filtered.copy()
monthly["월"] = monthly[COL_DATE].dt.strftime("%Y-%m")
monthly = monthly.groupby(["월", COL_FAC], as_index=False)[COL_GEN].sum()
fig_bar = px.bar(
    monthly,
    x="월",
    y=COL_GEN,
    color=COL_FAC,
    labels={COL_GEN: "발전량(kWh)", COL_FAC: "발전설비"},
)
st.plotly_chart(fig_bar, use_container_width=True)


# ------------------------------------------------------------
# 6. 데이터 표
# ------------------------------------------------------------
st.subheader("📋 데이터 표")
table = filtered.sort_values(COL_DATE).copy()
table[COL_DATE] = table[COL_DATE].dt.strftime("%Y-%m-%d")
st.dataframe(table, use_container_width=True, hide_index=True)
