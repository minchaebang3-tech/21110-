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

        <ol>
            <li>발전설비를 선택한다.</li>
            <li>원하는 날짜 범위를 선택한다.</li>
            <li>총 발전량과 일평균 발전량을 확인한다.</li>
            <li>그래프를 통해 날짜에 따른 발전량 변화를 확인한다.</li>
        </ol>

        </div>
        """,
        "info": None
    },

    {
        "key": "monthly",
        "button": "월별 발전량",
        "desc": "월별 발전량 비교 방법",
        "title": "📊 월별 발전량",
        "html": """
        <div class="guide-box">

        <b>무엇을 볼 수 있나?</b>

        <p>
        날짜별 데이터를 월 단위로 묶어 월별 총 발전량을
        비교할 수 있다.
        </p>

        <b>사용 방법</b>

        <ol>
            <li>비교할 발전설비를 선택한다.</li>
            <li>시작 월과 종료 월을 선택한다.</li>
            <li>월별 막대그래프를 확인한다.</li>
        </ol>

        </div>
        """,
        "info": None
    },

    {
        "key": "ranking",
        "button": "발전설비별 순위",
        "desc": "설비별 발전량 순위 확인 방법",
        "title": "🏆 발전설비별 순위",
        "html": """
        <div class="guide-box">

        <b>무엇을 볼 수 있나?</b>

        <p>
        선택한 기간 동안 각 발전설비가 생산한
        총 발전량을 비교할 수 있다.
        </p>

        <b>사용 방법</b>

        <ol>
            <li>비교할 기간을 선택한다.</li>
            <li>표시할 발전설비의 개수를 선택한다.</li>
            <li>막대그래프에서 발전량 순위를 확인한다.</li>
            <li>아래 표에서 전체 발전설비의 순위를 확인한다.</li>
        </ol>

        </div>
        """,
        "info": None
    },

    {
        "key": "region",
        "button": "지역별 발전량",
        "desc": "지역별 발전량 비교 방법",
        "title": "🗺️ 지역별 발전량",
        "html": """
        <div class="guide-box">

        <b>무엇을 볼 수 있나?</b>

        <p>
        발전설비 이름을 기준으로 지역을 추정하여
        지역별 총 발전량을 비교한다.
        </p>

        </div>
        """,
        "info": (
            "💡 이 데이터에는 별도의 지역 컬럼이 없기 때문에 "
            "발전설비 이름의 앞부분을 기준으로 지역을 추정한다."
        )
    },

    {
        "key": "util",
        "button": "평균 이용률",
        "desc": "이용률이 무엇이고 어떻게 계산하는지",
        "title": "⚡ 평균 이용률이란?",
        "html": """
        <div class="guide-box">

        평균 이용률은 발전설비가 일정 기간 동안
        설비용량을 얼마나 활용했는지를 나타내는 값이다.

        <br><br>

        <b>계산 방법</b>

        <br><br>

        평균 이용률 =
        실제 발전량 ÷ (설비용량 × 24시간) × 100

        <br><br>

        값이 높을수록 해당 기간 동안
        설비용량을 더 많이 활용하여 발전했다는 것을 의미한다.

        </div>
        """,
        "info": None
    },

    {
        "key": "heatmap",
        "button": "월별 이용률 히트맵",
        "desc": "히트맵 보는 법과 이미지 저장",
        "title": "🔥 월별 이용률 히트맵",
        "html": """
        <div class="guide-box">

        <b>무엇을 볼 수 있나?</b>

        <p>
        발전설비별 이용률을 월마다 색으로 나타낸 표이다.
        가로는 월, 세로는 발전설비이고 색이 진할수록
        해당 달에 설비용량을 더 많이 활용했다는 뜻이다.
        빈칸은 그 달의 데이터가 없다는 의미이다.
        </p>

        <b>사용 방법</b>

        <ol>
            <li>왼쪽 사이드바에서 비교할 발전설비를 선택한다.</li>
            <li>같은 곳에서 보고 싶은 월을 하나씩 골라 선택한다.</li>
            <li>히트맵 위의 결과 요약에서 이용률이 가장 높은 설비와 낮은 설비를 확인한다.</li>
            <li>그래프 오른쪽 위 카메라 아이콘을 누르면 결과 요약이 포함된 이미지로 저장할 수 있다.</li>
        </ol>

        <b>이름 앞에 ⚠️가 붙은 설비</b>

        <p>
        이용률이 100%를 넘는 달이 있는 설비이다.
        설비용량을 24시간 내내 최대로 가동해도 100%가 최대이므로
        원본 데이터의 설비용량을 확인해야 한다.
        이 설비들은 결과 요약 계산에서는 제외하고 그래프에는 그대로 표시한다.
        </p>

        </div>
        """,
        "info": None
    },

]

SECTION_MAP = {
    s["key"]: s
    for s in SECTIONS
}


# ============================================================
# 화면 상태 (메인 앱의 page와 겹치지 않게 다른 이름 사용)
# ============================================================
if "guide_section" not in st.session_state:
    st.session_state.guide_section = "home"


def go_guide(key):

    st.session_state.guide_section = key

    st.rerun()


current = st.session_state.guide_section

if current != "home" and current not in SECTION_MAP:
    current = "home"


# ============================================================
# 설명서 목록 화면
# ============================================================
if current == "home":

    show_html(
        """
        <div class="guide-box">

            <h1>📖 발전량 프로그램 소개 및 사용 설명서</h1>

            <p>
                공공데이터를 활용하여 신재생에너지 발전량을
                다양한 기준으로 확인하고 비교할 수 있는
                데이터 분석 프로그램
            </p>

        </div>
        """
    )

    st.subheader("🌿 보고 싶은 설명서 선택!")

    st.write(
        "궁금한 기능을 선택하면 "
        "그 기능의 설명서만 볼 수 있습니다."
    )

    st.write("")

    for i in range(0, len(SECTIONS), 2):

        cols = st.columns(2)

        for col, sec in zip(cols, SECTIONS[i:i + 2]):

            with col:

                if st.button(
                    f"{sec['button']}\n\n{sec['desc']}",
                    key=f"guide_{sec['key']}",
                    use_container_width=True
                ):

                    go_guide(sec["key"])

        st.write("")

    show_html(
        """
        <div class="source-box">

            ☀️ <b>데이터 출처</b><br><br>

            공공데이터포털(data.go.kr)<br>
            한국중부발전(주) 신재생에너지 발전량

        </div>
        """
    )


# ============================================================
# 설명서 내용 화면
# ============================================================
else:

    if st.button(
        "← 설명서 목록으로",
        key="guide_back"
    ):

        go_guide("home")

    st.divider()

    sec = SECTION_MAP[current]

    st.header(sec["title"])

    show_html(sec["html"])

    if sec["info"]:

        st.info(sec["info"])
