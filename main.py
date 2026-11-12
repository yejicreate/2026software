import streamlit as st
import time
import pandas as pd
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="학생용 학습 앱", page_icon="⏱️", layout="centered")

# 사이드바 메뉴 구성
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio("원하는 기능을 선택하세요", ["공부타이머", "오늘 할 일", "공부회고"])

if menu == "공부타이머":
    # Session State 초기화
    if "running" not in st.session_state:
        st.session_state.running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "elapsed_time" not in st.session_state:
        st.session_state.elapsed_time = 0  # 초 단위 저장
    if "records" not in st.session_state:
        st.session_state.records = []  # 과목별 학습 기록 저장

    # 타이머 조작 함수 정의
    def start_timer():
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.start_time = time.time() - st.session_state.elapsed_time

    def pause_timer():
        if st.session_state.running:
            st.session_state.running = False
            st.session_state.elapsed_time = time.time() - st.session_state.start_time

    def reset_timer():
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.elapsed_time = 0

    def save_record(subject):
        if st.session_state.elapsed_time > 0:
            minutes = int(st.session_state.elapsed_time // 60)
            seconds = int(st.session_state.elapsed_time % 60)
            formatted_time = f"{minutes}분 {seconds}초"
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.session_state.records.append({
                "날짜": current_date,
                "과목": subject,
                "학습 시간": formatted_time,
                "초(sec)": int(st.session_state.elapsed_time)
            })
            st.toast(f"'{subject}' 학습 기록이 저장되었습니다! ({formatted_time})", icon="✅")
            reset_timer()
        else:
            st.warning("저장할 학습 시간이 없습니다.")

    # 앱 화면 구성
    st.title("⏱️ 학생용 학습 타이머")

    # 1. 과목 선택 및 입력 영역
    subject_list = ["국어", "수학", "영어", "과학", "사회", "기타"]
    selected_subject = st.selectbox("📖 공부할 과목을 선택하세요", subject_list)
    if selected_subject == "기타":
        custom_subject = st.text_input("직접 과목명을 입력하세요", placeholder="예: 코딩")
        if custom_subject:
            selected_subject = custom_subject

    st.markdown("---")

    # 2. 타이머 실시간 계산
    if st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time

    # 시간 형식화 (HH:MM:SS)
    total_seconds = int(st.session_state.elapsed_time)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    time_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # 타이머 시각적 대형 출력
    st.markdown(
        f"""
        <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 15px; margin-bottom: 25px;">
            <h1 style="font-size: 70px; color: #1E88E5; margin: 0;">{time_display}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. 조작 버튼 (시작, 일시정지, 초기화)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("▶️ 시작", on_click=start_timer, use_container_width=True, disabled=st.session_state.running)

    with col2:
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True, disabled=not st.session_state.running)

    with col3:
        st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

    # 4. 저장 버튼
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"💾 '{selected_subject}' 과목으로 기록 저장하기", use_container_width=True):
        save_record(selected_subject)

    st.markdown("---")

    # 5. 과목별 기록 조회 영역
    st.subheader("📊 오늘의 과목별 학습 기록")

    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        
        # 총 학습 시간 요약 계산
        total_sec_sum = df["초(sec)"].sum()
        total_h = total_sec_sum // 3600
        total_m = (total_sec_sum % 3600) // 60
        st.metric("오늘의 누적 학습 시간", f"{total_h}시간 {total_m}분")

        # 테이블 출력
        st.dataframe(df[["날짜", "과목", "학습 시간"]], use_container_width=True)
        
        # 기록 전체 삭제 버튼
        if st.button("🗑️ 전체 기록 삭제"):
            st.session_state.records = []
            st.rerun()
    else:
        st.info("아직 기록된 학습 시간이 없습니다. 타이머로 공부 시간을 측정하고 저장해보세요!")

    # 타이머가 동작 중일 때 1초마다 화면 갱신
    if st.session_state.running:
        time.sleep(1)
        st.rerun()

elif menu == "오늘 할 일":
    st.title("📝 오늘 할 일")

elif menu == "공부회고":
    st.title("✏️ 공부회고")
