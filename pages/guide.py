import streamlit as st


# ============================================================
# 페이지 기본 설정
# ============================================================
st.set_page_config(
    page_title="사용 설명서",
    page_icon="📖",
    layout="wide"
)


# ============================================================
# HTML 출력 함수
# → 줄 앞 공백과 빈 줄을 지워서
#   HTML이 코드 블록으로 오인되어 화면에 그대로 뜨는 문제를 막음
# ============================================================
def show_html(body):

    body = "\n".join(
        line.strip()
        for line in body.split("\n")
        if line.strip()
    )

    st.markdown(
        body,
        unsafe_allow_html=True
    )


# ============================================================
# 디자인
# ============================================================
st.markdown("""
<style>

    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    h1, h2, h3, p, li, label {
        font-family: 'Gowun Dodum', sans-serif;
    }

    .stApp {
        background: linear-gradient(
            180deg,
            #ECFDF3 0%,
            #F7FEF9 40%,
            #FFFFFF 100%
        );
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    h1 {
        color: #14532D;
        font-weight: 800;
    }

    h2, h3 {
        color: #16A34A;
    }

    p {
        color: #3F5F4B;
    }

    /* 버튼 */
    .stButton > button {
        width: 100%;
        min-height: 90px;
        border-radius: 20px;
        border: 1.5px solid #BBF7D0;
        background-color: white;
        color: #14532D;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.10);
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #22C55E;
        background-color: #DCFCE7;
        color: #14532D;
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(34, 197, 94, 0.18);
    }

    /* 목록으로 돌아가기 버튼은 작게 */
    .st-key-guide_back button {
        min-height: 3rem;
    }

    .guide-box {
        background-color: white;
        border: 1px solid #BBF7D0;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.08);
    }

    .tip-box {
        background-color: #ECFDF3;
        border: 1px solid #BBF7D0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
    }

    .source-box {
        background-color: #F7FEE7;
        border: 1px solid #D9F99D;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    /* 안내 메시지(st.info) */
    [data-testid="stAlert"] {
        background-color: #ECFDF3;
        color: #166534;
        border: 1px solid #BBF7D0;
        border-radius: 14px;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #F0FDF4;
        border-right: 1px solid #BBF7D0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# 설명서 목록
# ============================================================
SECTIONS = [

    {
        "key": "intro",
        "button": "프로그램 소개",
        "desc": "이 프로그램이 하는 일",
        "title": "🌿 프로그램 소개",
        "html": """
        <div class="guide-box">

        이 프로그램은 한국중부발전의 신재생에너지 발전량
        공공데이터를 활용하여 발전량을 시각적으로 분석한다.

        <br><br>

        사용자는 날짜와 발전설비를 선택하여 데이터를 확인하거나,
        월별·발전설비별·지역별로 발전량을 비교할 수 있다.

        </div>
        """,
        "info": None
    },

    {
        "key": "data",
        "button": "데이터 정보",
        "desc": "데이터 출처와 항목",
        "title": "📊 데이터 정보",
        "html": """
        <div class="guide-box">

        <b>데이터 출처</b><br>
        공공데이터포털(data.go.kr)<br>
        한국중부발전(주) 신재생에너지 발전량

        <br><br>

        <b>주요 데이터 항목</b>

        <ul>
            <li>연월일 : 발전량이 기록된 날짜</li>
            <li>발전설비 : 발전량을 생산한 발전설비</li>
            <li>설비용량(kW) : 해당 발전설비의 설비용량</li>
            <li>발전량(kWh) : 해당 날짜에 생산된 전력량</li>
        </ul>

        </div>
        """,
        "info": None
    },

    {
        "key": "daily",
        "button": "일별 발전량",
        "desc": "날짜별 발전량 확인 방법",
        "title": "📈 일별 발전량",
        "html": """
        <div class="guide-box">

        <b>무엇을 볼 수 있나?</b>

        <p>
        날짜별 발전량의 변화를 그래프로 확인할 수 있다.
        여러 발전설비를 선택하면 발전설비별 발전량을
        동시에 비교할 수 있다.
        </p>

        <b>사용 방법</b>
