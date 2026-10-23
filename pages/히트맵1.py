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

    num =
