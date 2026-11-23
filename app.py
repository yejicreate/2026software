import streamlit as st
from datetime import datetime, date
import hashlib

# 페이지 기본 설정
st.set_page_config(
    page_title="Remember me · 기억과 향기의 보존",
    page_icon="🔮",
    layout="centered"
)

# 연한 초록색 배경 + 선명한 글자 대비 + 인사이드 아웃 '기억 구슬' 스타일
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700&family=Pretendard:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #18281c;
    }

    /* 전체 앱 배경: 연한 초록색 */
    .stApp {
        background: linear-gradient(180deg, #e8f3ea 0%, #dcebe0 100%);
        color: #18281c;
    }

    h1, h2, h3, h4, p, label, span, div {
        color: #18281c;
    }

    h1, h2, h3, .serif-title {
        font-family: 'Noto Serif KR', serif;
        color: #132217;
        letter-spacing: -0.02em;
    }

    /* 입력창, 텍스트영역, 셀렉트박스 배경과 글자색 명시 (흰/검 겹침 방지) */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input {
        background-color: #ffffff !important;
        color: #18281c !important;
        border: 1px solid #9ab8a1 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #6b8270 !important;
    }

    /* 폼 내부 및 탭/익스팬더 가독성 */
    div[data-testid="stForm"] {
        background-color: #f6fbf7;
        border: 1px solid #b7d1bc;
        border-radius: 16px;
        padding: 18px 20px;
    }

    /* 상단 헤더 배너 */
    .remember-banner {
        background: linear-gradient(135deg, #f5fbf6 0%, #e4f2e7 100%);
        border: 1px solid #b4cfb9;
        border-radius: 22px;
        padding: 24px 26px;
        margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(24, 40, 28, 0.06);
    }

    .remember-sub {
        color: #354f3b;
        font-size: 0.95rem;
        margin-top: 6px;
        line-height: 1.55;
    }

    /* 인사이드 아웃 기억 구슬(Memory Orb) 스타일 */
    .orb-row {
        display: flex;
        justify-content: space-around;
        align-items: flex-start;
        gap: 10px;
        background: #f5fbf6;
        border: 1px solid #b7d1bc;
        border-radius: 20px;
        padding: 16px 12px;
        margin: 12px 0 20px 0;
        box-shadow: 0 4px 14px rgba(24, 40, 28, 0.05);
    }

    .orb-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
    }

    .memory-orb {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.45rem;
        margin-bottom: 7px;
        border: 2px solid rgba(255, 255, 255, 0.85);
        box-shadow:
            inset -6px -6px 12px rgba(0, 0, 0, 0.16),
            inset 6px 6px 12px rgba(255, 255, 255, 0.78),
            0 6px 14px rgba(24, 40, 28, 0.16);
    }

    .orb-gold {
        background: radial-gradient(circle at 30% 30%, #fff0a6, #f2b705 68%, #b88200);
    }
    .orb-blue {
        background: radial-gradient(circle at 30% 30%, #bce6ff, #3b9ae1 68%, #1d5f96);
    }
    .orb-green {
        background: radial-gradient(circle at 30% 30%, #c8f5d0, #3aa856 68%, #1f6932);
    }
    .orb-coral {
        background: radial-gradient(circle at 30% 30%, #ffd0c4, #eb6b56 68%, #9e3828);
    }
    .orb-purple {
        background: radial-gradient(circle at 30% 30%, #e6d1ff, #9b6ee0 68%, #5b3696);
    }

    .orb-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #18281c;
        line-height: 1.25;
    }

    .orb-active-ring {
        outline: 3px solid #2b6e3f;
        outline-offset: 2px;
    }

    /* 오늘의 질문 카드 */
    .question-card {
        background: #
