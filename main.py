import csv
import glob
import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# 기본 페이지 설정 (반드시 streamlit 명령 중 가장 먼저!)
# ------------------------------------------------------------
st.set_page_config(page_title="재생에너지 발전량 대시보드", layout="wide")
st.title("☀️ 한국중부발전 신재생에너지 발전량 대시보드")
st.caption("출처: 공공데이터포털(data.go.kr) 한국중부발전 신재생에너지 발전량 (일별)")

# 이 코드가 들어 있는 폴더 (data.csv도 같은 폴더에 있어야 해요)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 앱 안에서 쓸 컬럼 이름 (파일의 컬럼 이름이 조금 달라도 여기에 맞춰 바꿔요)
COL_DATE = "연월일"
COL_FAC = "발전설비"
COL_CAP = "설비용량(kW)"
COL_GEN = "발전량(kWh)"


class DataError(Exception):
    """데이터 파일 문제를 사용자에게 알려주기 위한 오류"""


# ------------------------------------------------------------
# 1. 데이터 파일 찾기
# ------------------------------------------------------------
def find_data_file():
    # 1순위: data.csv
    main_path = os.path.join(BASE_DIR, "data.csv")
    if os.path.exists(main_path):
        return main_path, False

    # 2순위: 같은 폴더의 다른 표 파일 (이름을 잘못 올렸을 때 대비)
    candidates = []
    for pattern in ("*.csv", "*.xlsx", "*.xls"):
        candidates += glob.glob(os.path.join(BASE_DIR, pattern))
    candidates = sorted(candidates)
    if candidates:
        return candidates[0], True

    raise FileNotFoundError("data.csv")


# ------------------------------------------------------------
# 2. 파일을 '줄 목록'으로 읽기 (제목줄 위에 설명이 있어도 OK)
# ------------------------------------------------------------
def find_header_index(rows):
    """'연월일'과 '발전량'이 함께 들어 있는 줄 = 제목줄 위치 찾기"""
    for i, row in enumerate(rows[:100]):
        cells = [str(c).strip() for c in row]
        has_date = any(c.startswith("연월일") for c in cells)
        has_gen = any(c.startswith("발전량") for c in cells)
        if has_date and has_gen:
            return i
    return None


def rows_to_df(rows, header_idx):
    header = [str(c).strip() for c in rows[header_idx]]
    n = len(header)
    body = []
    for r in rows[header_idx + 1:]:
        r = list(r)
        r = (r + [""] * n)[:n]  # 칸 수를 제목줄에 맞추기
        body.append(r)
    return pd.DataFrame(body, columns=header)


def read_table(path):
    with open(path, "rb") as f:
        head = f.read(8)

    # (가) 엑셀 파일 (이름만 data.csv로 바꾼 경우 포함)
    if head[:2] == b"PK" or head[:4] == b"\xd0\xcf\x11\xe0":
        engine = "openpyxl" if head[:2] == b"PK" else "xlrd"
        raw = pd.read_excel(path, header=None, engine=engine)
        raw = raw.astype(object).where(raw.notna(), "")
        rows = raw.values.tolist()
        idx = find_header_index(rows)
        if idx is None:
            raise DataError(
                "엑셀 파일에서 제목줄(연월일, 발전량 ...)을 찾지 못했어요."
            )
        return rows_to_df(rows, idx)

    # (나) 글자로 된 파일(CSV): 인코딩과 구분 기호를 하나씩 시도
    with open(path, "rb") as f:
        data = f.read()

    for enc in ("utf-8-sig", "cp949", "utf-16"):
        try:
            text = data.decode(enc)
        except UnicodeDecodeError:
            continue
        for sep in (",", "\t", ";", "|"):
            try:
                rows = list(csv.reader(io.StringIO(text), delimiter=sep))
            except Exception:
                continue
            idx = find_header_index(rows)
            if idx is not None:
                return rows_to_df(rows, idx)

    raise DataError(
        "파일에서 제목줄(연월일, 발전설비, 설비용량, 발전량)을 찾지 못했어요. "
        f"파일 시작 바이트: {head!r}"
    )


# ------------------------------------------------------------
# 3. 날짜 / 숫자 정리
# ------------------------------------------------------------
def parse_dates(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    t = series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # 20231101 같은 8자리 숫자
    parsed = pd.to_datetime(t, format="%Y%m%d", errors="coerce")

    # 엑셀 날짜 번호 (예: 45231)
    num = pd.to_numeric(t, errors="coerce")
    serial = pd.to_datetime(
        num.where(num.between(20000, 80000)), unit="D", origin="1899-12-30"
    )
    parsed = parsed.fillna(serial)

    # 그 밖의 형태 (2023-11-01, 2023.11.01 등)는 자동 인식
    if parsed.isna().any():
        auto = pd.to_datetime(t.where(parsed.isna()), errors="coerce")
        parsed = parsed.fillna(auto)
    return parsed


def to_number(series):
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce")


# ------------------------------------------------------------
# 4. 데이터 불러오기 + 정리 (한 번 읽으면 저장해 두는 캐시)
# ------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = read_table(path)

    # 컬럼 이름 통일 (단위가 있든 없든 OK)
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
    df = df.loc[:, ~df.columns.duplicated()]  # 같은 이름이 두 번이면 앞의 것만

    missing = [c for c in (COL_DATE, COL_FAC, COL_CAP, COL_GEN) if c not in df.columns]
    if missing:
        raise DataError(
            f"필요한 컬럼이 없어요: {', '.join(missing)} / 파일의 컬럼: {list(df.columns)}"
        )

    df = df[[COL_DATE, COL_FAC, COL_CAP, COL_GEN]].copy()
    df[COL_DATE] = parse_dates(df[COL_DATE])
    df[COL_CAP] = to_number(df[COL_CAP])
    df[COL_GEN] = to_number(df[COL_GEN])
    df[COL_FAC] = df[COL_FAC].astype(str).str.strip()

    # 날짜/발전량/설비 이름이 비어 있는 행은 제거
    df = df.dropna(subset=[COL_DATE, COL_GEN])
    df = df[~df[COL_FAC].isin(["", "nan", "None"])]

    if df.empty:
        raise DataError("정리하고 나니 남은 데이터가 없어요. 날짜/발전량 값을 확인해 주세요.")
    return df.sort_values(COL_DATE).reset_index(drop=True)


# ------------------------------------------------------------
# 5. 화면에 불러오기 (문제가 생기면 이유를 안내)
# ------------------------------------------------------------
try:
    data_path, used_other_file = find_data_file()
    df = load_data(data_path)
except FileNotFoundError:
    st.error(
        "데이터 파일을 찾을 수 없어요. GitHub 저장소에 data.csv를 올렸는지, "
        "이름이 정확히 data.csv인지 확인해 주세요."
    )
    st.stop()
except DataError as e:
    st.error(f"데이터 파일 문제: {e}")
    st.stop()
except Exception as e:
    st.error(f"데이터를 읽는 중 문제가 생겼어요: {type(e).__name__}: {e}")
    st.stop()

if used_other_file:
    st.info(f"data.csv가 없어서 '{os.path.basename(data_path)}' 파일을 대신 사용했어요.")


# ------------------------------------------------------------
# 6. 사이드바: 발전설비 선택 + 기간 선택
# ------------------------------------------------------------
st.sidebar.header("🔎 조건 선택")

facilities = sorted(df[COL_FAC].unique())
selected = st.sidebar.multiselect("발전설비", facilities, default=facilities)

min_date = df[COL_DATE].min().date()
max_date = df[COL_DATE].max().date()
period = st.sidebar.date_input(
    "기간",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# 시작일/종료일을 둘 다 골랐는지 확인
if not isinstance(period, (tuple, list)) or len(period) != 2:
    st.warning("기간의 시작일과 종료일을 모두 선택해 주세요.")
    st.stop()

if len(selected) == 0:
    st.warning("발전설비를 하나 이상 선택해 주세요.")
    st.stop()

start = pd.to_datetime(period[0])
end = pd.to_datetime(period[1])

filtered = df[
    (df[COL_FAC].isin(selected))
    & (df[COL_DATE] >= start)
    & (df[COL_DATE] <= end)
]

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없어요. 조건을 바꿔 보세요.")
    st.stop()


# ------------------------------------------------------------
# 7. 카드 3개: 총 발전량 / 일평균 발전량 / 평균 이용률
# ------------------------------------------------------------
total_gen = filtered[COL_GEN].sum()

# 일평균 = 총 발전량 ÷ 날짜 수
num_days = filtered[COL_DATE].nunique()
daily_avg = total_gen / num_days if num_days > 0 else 0

# 이용률 = 발전량 ÷ (설비용량 × 24시간)
# 설비용량이 비어 있거나 0인 행은 계산에서 제외
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
# 8. 일별 발전량 선 그래프
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
st.plotly_chart(fig_line)


# ------------------------------------------------------------
# 9. 월별 총 발전량 막대 그래프
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
st.plotly_chart(fig_bar)


# ------------------------------------------------------------
# 10. 데이터 표
# ------------------------------------------------------------
st.subheader("📋 데이터 표")
table = filtered.copy()
table[COL_DATE] = table[COL_DATE].dt.strftime("%Y-%m-%d")
st.dataframe(table, hide_index=True)
