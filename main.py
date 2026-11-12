import streamlit as st
import time
import pandas as pd
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="학생용 학습 앱", page_icon="⏱️", layout="centered")

# 사이드바 메뉴 구성
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio("원하는 기능을 선택하세요", ["공부타이머", "오늘 할 일", "공부회고"])

# 공통 과목 리스트
subject_list = ["국어", "영어", "수학", "사회", "과학", "한국사", "소생", "과탐실", "기타"]

# 1. 공부타이머 메뉴
if menu == "공부타이머":
    if "running" not in st.session_state:
        st.session_state.running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "elapsed_time" not in st.session_state:
        st.session_state.elapsed_time = 0
    if "records" not in st.session_state:
        st.session_state.records = []

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

    st.title("⏱️ 학생용 학습 타이머")

    selected_subject = st.selectbox("📖 공부할 과목을 선택하세요", subject_list)
    if selected_subject == "기타":
        custom_subject = st.text_input("직접 과목명을 입력하세요", placeholder="예: 프로그래밍")
        if custom_subject:
            selected_subject = custom_subject

    st.markdown("---")

    if st.session_state.running:
        st.session_state.elapsed_time = time.time() - st.session_state.start_time

    total_seconds = int(st.session_state.elapsed_time)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    time_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    st.markdown(
        f"""
        <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 15px; margin-bottom: 25px;">
            <h1 style="font-size: 70px; color: #1E88E5; margin: 0;">{time_display}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("▶️ 시작", on_click=start_timer, use_container_width=True, disabled=st.session_state.running)
    with col2:
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True, disabled=not st.session_state.running)
    with col3:
        st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"💾 '{selected_subject}' 과목으로 기록 저장하기", use_container_width=True):
        save_record(selected_subject)

    st.markdown("---")
    st.subheader("📊 오늘의 과목별 학습 기록")

    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        total_sec_sum = df["초(sec)"].sum()
        total_h = total_sec_sum // 3600
        total_m = (total_sec_sum % 3600) // 60
        st.metric("오늘의 누적 학습 시간", f"{total_h}시간 {total_m}분")

        st.dataframe(df[["날짜", "과목", "학습 시간"]], use_container_width=True)
        
        if st.button("🗑️ 전체 기록 삭제"):
            st.session_state.records = []
            st.rerun()
    else:
        st.info("아직 기록된 학습 시간이 없습니다. 타이머로 공부 시간을 측정하고 저장해보세요!")

    if st.session_state.running:
        time.sleep(1)
        st.rerun()

# 2. 오늘 할 일 메뉴
elif menu == "오늘 할 일":
    st.title("📝 오늘 할 일")

    if "todo_list" not in st.session_state:
        st.session_state.todo_list = []

    with st.form("todo_form", clear_on_submit=True):
        todo_subject = st.selectbox("📖 과목 선택", subject_list)
        todo_task = st.text_input("할 일을 입력하세요", placeholder="예: 수학 문제집 3쪽 풀기")
        submit_button = st.form_submit_button("➕ 추가")

        if submit_button:
            if todo_task.strip():
                st.session_state.todo_list.append({
                    "과목": todo_subject,
                    "할 일": todo_task,
                    "완료": False
                })
                st.success(f"'{todo_task}' 항목이 추가되었습니다.")
            else:
                st.warning("할 일을 입력해주세요.")

    st.markdown("---")
    st.subheader("📋 할 일 목록")

    if st.session_state.todo_list:
        for idx, item in enumerate(st.session_state.todo_list):
            cols = st.columns([0.1, 0.2, 0.6, 0.1])
            with cols[0]:
                is_checked = st.checkbox("", value=item["완료"], key=f"todo_chk_{idx}")
                st.session_state.todo_list[idx]["완료"] = is_checked
            with cols[1]:
                st.markdown(f"**[{item['과목']}]**")
            with cols[2]:
                if is_checked:
                    st.markdown(f"<span style='text-decoration: line-through; color: gray;'>{item['할 일']}</span>", unsafe_allow_html=True)
                else:
                    st.write(item['할 일'])
            with cols[3]:
                if st.button("❌", key=f"del_{idx}"):
                    st.session_state.todo_list.pop(idx)
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ 완료된 항목 일괄 삭제"):
            st.session_state.todo_list = [item for item in st.session_state.todo_list if not item["완료"]]
            st.rerun()
    else:
        st.info("등록된 할 일이 없습니다. 과목과 할 일을 추가해보세요!")

# 3. 공부회고 메뉴
elif menu == "공부회고":
    st.title("✏️ 공부회고")

    if "retrospectives" not in st.session_state:
        st.session_state.retrospectives = []
    if "show_review_input" not in st.session_state:
        st.session_state.show_review_input = False

    # 총 공부 시간 계산 (타이머 기록 연동)
    total_h, total_m = 0, 0
    if "records" in st.session_state and st.session_state.records:
        df_rec = pd.DataFrame(st.session_state.records)
        total_sec_sum = df_rec["초(sec)"].sum()
        total_h = total_sec_sum // 3600
        total_m = (total_sec_sum % 3600) // 60

    # 총 공부시간 옆에 '추가' 버튼 배치
    metric_col, btn_col = st.columns([0.7, 0.3])
    with metric_col:
        st.metric("오늘의 총 공부 시간", f"{total_h}시간 {total_m}
