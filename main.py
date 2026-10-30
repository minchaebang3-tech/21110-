import csv
import glob
import io
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


# ============================================================
# 그래프 기본 색 (초록 계열)
# → 모든 그래프에 한 번에 적용됨
# ============================================================
pio.templates["eco"] = go.layout.Template(
    layout=go.Layout(
        colorway=[
            "#047857",
            "#10B981",
            "#34D399",
            "#065F46",
            "#6EE7B7",
            "#059669",
            "#A7F3D0",
            "#15803D"
        ],
        font=dict(
            family="Gowun Dodum, sans-serif",
            color="#244B38"
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FFFB",
        xaxis=dict(
            gridcolor="#E5F5EC",
            zerolinecolor="#CDEBDD"
        ),
        yaxis=dict(
            gridcolor="#E5F5EC",
            zerolinecolor="#CDEBDD"
        )
    )
)

pio.templates.default = "plotly+eco"

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

.block-container {
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

h1 {
    color: #064E3B !important;
    font-weight: 900 !important;
    letter-spacing: -0.5px;
}

h2, h3 {
    color: #047857 !important;
    font-weight: 800 !important;
}

p, li, label {
    color: #365F4B;
    line-height: 1.7;
}
