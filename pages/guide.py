import streamlit as st

# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="사용 설명서",
    page_icon="🌿",
    layout="wide"
)

# ==================================================
# 디자인
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, [class*="css"] {
    font-family: 'Gowun Dodum', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 5% 5%, #D1FAE5 0%, transparent 25%),
        radial-gradient(circle at 95% 90%, #BBF7D0 0%, transparent 25%),
        linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 45%, #FFFFFF 100%);
}

/* 전체 화면 */
.block-container {
    max-width: 1150px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

/* 제목 */
h1 {
    color: #064E3B !important;
    font-weight: 900 !important;
    letter-spacing: -1px;
}

h2 {
    color: #065F46 !important;
    font-weight: 800 !important;
}

h3 {
    color: #047857 !important;
    font-weight: 700 !important;
}

p, li {
    color: #365F4B;
    line-height: 1.8;
}

/* 구분선 */
hr {
    border-color: #A7F3D0 !important;
}

/* 메인 소개 영역 */
.main-banner {
    background: linear-gradient(120deg, #064E3B 0%, #047857 55%, #10B981 100%);
    padding: 38px 40px;
    border-radius: 25px;
    margin-bottom: 30px;
    box-shadow: 0 10px 25px rgba(6, 78, 59, 0.18);
    position: relative;
    overflow: hidden;
}

.main-banner h1 {
    color: white !important;
    font-size: 2.2rem;
    margin-bottom: 12px;
}

.main-banner p {
    color: #D1FAE5 !important;
    font-size: 1.05rem;
    margin-bottom: 0;
}

/* 카드 디자인 */
.guide-box {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid #A7F3D0;
    border-radius: 20px;
    padding: 24px;
    margin: 14px 0;
    box-shadow: 0 5px 16px rgba(5, 150, 105, 0.07);
    transition: all 0.2s ease;
}

.guide-box:hover {
    border-color: #34D399;
    box-shadow: 0 8px 20px rgba(5, 150, 105, 0.12);
}

/* 데이터 정보 카드 */
.data-box {
    background: linear-gradient(135deg, #D1FAE5, #ECFDF5);
    border: 1px solid #6EE7B7;
    border-radius: 18px;
    padding: 22px;
    height: 100%;
}

/* 기능 선택 버튼 */
.stButton > button {
    width: 100%;
    min-height: 105px;
    border-radius: 20px;
    border: 1px solid #86EFAC;
    background: linear-gradient(145deg, #FFFFFF, #ECFDF5);
    color: #065F46;
    font-weight: bold;
    font-size: 17px;
    box-shadow: 0 5px 14px rgba(5, 150, 105, 0.09);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #047857, #059669);
    border-color: #047857;
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(5, 150, 105, 0.2);
}

/* 돌아가기 버튼 */
.stButton > button[kind="secondary"] {
    min-height: 48px;
    background: #D1FAE5;
    border: 1px solid #6EE7B7;
    color: #065F46;
}

/* 안내 박스 */
.tip-box {
    background: #D1FAE5;
    border-left: 5px solid #059669;
    border-radius: 12px;
    padding: 17px 20px;
    margin: 15px 0;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #D1FAE5, #ECFDF5);
}

/* 정보 박스 */
[data-testid="stAlert"] {
    border-radius: 14px;
}

/* 선택 영역 */
[data-testid="stSelectbox"] > div > div {
    border-color: #86EFAC;
    border-radius: 12px;
}

/* 하단 여백 */
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 설명서 데이터
# ==================================================
SECTIONS = {
    "daily": {
        "button": "📈 일별 발전량",
        "desc": "날짜별 발전량과 평균 이용률 확인",
        "title": "📈 일별 발전량",
        "content": [
            ("무엇을 볼 수 있나?",
             "날짜별 발전량의 변화를 그래프로 확인할 수 있다. "
             "여러 발전설비를 선택하면 설비별 발전량을 동시에 비교할 수 있다."),
            ("사용 방법",
             "1. 발전설비를 선택한다.\n"
             "2. 원하는 날짜 범위를 선택한다.\n"
             "3. 총 발전량, 일평균 발전량, 평균 이용률을 확인한다.\n"
             "4. 그래프에서 날짜에 따른 발전량 변화를 확인한다."),
            ("평균 이용률이란?",
             "발전설비가 일정 기간 동안 설비용량을 얼마나 활용했는지를 나타내는 값이다.\n\n"
             "평균 이용률(%) = 실제 발전량 ÷ (설비용량 × 시간) × 100\n\n"
             "값이 높을수록 해당 기간 동안 설비용량을 더 많이 활용했다는 의미이다.")
        ]
    },

    "monthly": {
        "button": "📊 월별 발전량",
        "desc": "월별 발전량 비교 방법",
        "title": "📊 월별 발전량",
        "content": [
            ("무엇을 볼 수 있나?",
             "날짜별 데이터를 월 단위로 묶어 월별 총 발전량을 비교할 수 있다."),
            ("사용 방법",
             "1. 비교할 발전설비를 선택한다.\n"
             "2. 시작 월과 종료 월을 선택한다.\n"
             "3. 월별 막대그래프를 확인한다.")
        ]
    },

    "ranking": {
        "button": "🏆 발전설비별 순위",
        "desc": "설비별 발전량 순위 확인",
        "title": "🏆 발전설비별 순위",
        "content": [
            ("무엇을 볼 수 있나?",
             "선택한 기간 동안 각 발전설비가 생산한 총 발전량을 비교할 수 있다."),
            ("사용 방법",
             "1. 비교할 기간을 선택한다.\n"
             "2. 표시할 발전설비의 개수를 선택한다.\n"
             "3. 막대그래프에서 발전량 순위를 확인한다.\n"
             "4. 아래 표에서 전체 발전설비의 순위를 확인한다.")
        ]
    },

    "region": {
        "button": "🗺️ 지역별 발전량",
        "desc": "지역별 발전량 비교",
        "title": "🗺️ 지역별 발전량",
        "content": [
            ("무엇을 볼 수 있나?",
             "발전설비 이름을 기준으로 지역을 추정하여 지역별 총 발전량을 비교한다.")
        ],
        "info": "💡 데이터에 별도의 지역 컬럼이 없으므로 발전설비 이름의 앞부분을 기준으로 지역을 추정한다."
    },

    "heatmap": {
        "button": "🔥 월별 이용률 히트맵",
        "desc": "히트맵 확인 및 이미지 저장",
        "title": "🔥 월별 이용률 히트맵",
        "content": [
            ("무엇을 볼 수 있나?",
             "발전설비별 이용률을 월마다 색으로 나타낸 표이다.\n\n"
             "가로는 월, 세로는 발전설비이며 색이 진할수록 해당 달에 "
             "설비용량을 더 많이 활용했다는 의미이다.\n\n"
             "빈칸은 해당 월의 데이터가 없다는 뜻이다."),
            ("사용 방법",
             "1. 왼쪽 사이드바에서 비교할 발전설비를 선택한다.\n"
             "2. 보고 싶은 월을 선택한다.\n"
             "3. 결과 요약에서 이용률이 가장 높은 설비와 낮은 설비를 확인한다.\n"
             "4. 그래프 오른쪽 위 카메라 아이콘을 누르면 이미지를 저장할 수 있다."),
            ("⚠️ 표시가 붙은 발전설비",
             "이용률이 100%를 넘는 달이 있는 설비이다.\n\n"
             "설비용량을 24시간 내내 최대로 가동해도 이용률은 100%가 최대이므로 "
             "원본 데이터의 설비용량을 확인해야 한다.\n\n"
             "이 설비들은 결과 요약 계산에서는 제외하고 그래프에는 그대로 표시한다.")
        ]
    }
}


# ==================================================
# 화면 상태
# ==================================================
if "guide_section" not in st.session_state:
    st.session_state["guide_section"] = "home"


def go_home():
    st.session_state["guide_section"] = "home"


def go_section(key):
    st.session_state["guide_section"] = key


current = st.session_state["guide_section"]

if current not in SECTIONS and current != "home":
    current = "home"
    st.session_state["guide_section"] = "home"


# ==================================================
# 첫 화면
# ==================================================
if current == "home":

    st.markdown("""
    <div class="main-banner">
        <h1>🌿 발전량 프로그램 소개 및 사용 설명서</h1>
        <p>
        공공데이터를 활용하여 신재생에너지 발전량을<br>
        다양한 기준으로 확인하고 비교할 수 있는 데이터 분석 프로그램
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.header("🌱 프로그램 소개")

    st.markdown("""
    <div class="guide-box">
    이 프로그램은 한국중부발전의 신재생에너지 발전량
    공공데이터를 활용하여 발전량을 시각적으로 분석한다.

    <br><br>

    사용자는 날짜와 발전설비를 선택하여 데이터를 확인하거나,
    월별·발전설비별·지역별로 발전량을 비교할 수 있다.
    </div>
    """, unsafe_allow_html=True)

    st.header("📊 데이터 정보")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="data-box">
        <h3>🌍 데이터 출처</h3>
        <p>
        공공데이터포털(data.go.kr)<br>
        한국중부발전(주)<br>
        신재생에너지 발전량
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="data-box">
        <h3>📋 주요 데이터 항목</h3>
        <ul>
            <li>연월일 : 발전량이 기록된 날짜</li>
            <li>발전설비 : 발전량을 생산한 발전설비</li>
            <li>설비용량(kW) : 해당 발전설비의 설비용량</li>
            <li>발전량(kWh) : 해당 날짜에 생산된 전력량</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.header("🍃 보고 싶은 설명서 선택!")
    st.write("궁금한 기능을 선택하면 해당 기능의 설명서를 확인할 수 있다.")

    keys = list(SECTIONS.keys())

    for i in range(0, len(keys), 2):
        cols = st.columns(2)

        for j, col in enumerate(cols):
            index = i + j

            if index < len(keys):
                key = keys[index]
                section = SECTIONS[key]

                with col:
                    if st.button(
                        section["button"] + "\n\n" + section["desc"],
                        key="guide_" + key,
                        use_container_width=True
                    ):
                        go_section(key)
                        st.rerun()


# ==================================================
# 상세 설명서 화면
# ==================================================
else:

    if st.button("← 설명서 목록으로", key="guide_back"):
        go_home()
        st.rerun()

    st.divider()

    section = SECTIONS[current]

    st.header(section["title"])

    for heading, description in section["content"]:
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.subheader(heading)
        st.write(description)
        st.markdown('</div>', unsafe_allow_html=True)

    if section.get("info"):
        st.info(section["info"])

    st.write("")
    st.markdown("""
    <div style="
        text-align:center;
        padding:18px;
        background:linear-gradient(90deg,#D1FAE5,#ECFDF5);
        border-radius:15px;
        color:#065F46;
        font-weight:bold;">
        🌿 신재생에너지 발전량 데이터 분석 프로그램
    </div>
    """, unsafe_allow_html=True)
