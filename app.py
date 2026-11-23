import streamlit as st
from datetime import datetime, date
import hashlib

# 페이지 기본 설정
st.set_page_config(
    page_title="향기와 목소리 - 기억 보존 서비스",
    page_icon="🌿",
    layout="centered"
)

# 스타일 커스터마이징
st.markdown("""
    <style>
    .main-card {
        background-color: #f8f9fa;
        padding: 24px;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    .question-box {
        background-color: #fff3e0;
        padding: 20px;
        border-left: 5px solid #ff9800;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .scent-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        background-color: #e8f5e9;
        color: #2e7d32;
        font-weight: bold;
        margin: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "users" not in st.session_state:
    # 테스트용 기본 계정
    st.session_state.users = {
        "user1": {
            "password": "123",
            "name": "김민수",
            "birth": date(1985, 5, 15),
            "interests": "독서, 산책, 클래식 음악",
            "perfume": "이솝 테싯 오 드 퍼퓸",
            "softener": "다우니 화이트티와 릴리",
            "family_scent": "비 온 뒤 젖은 흙냄새와 은은한 우디 향이 섞인 포근한 냄새"
        }
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "records" not in st.session_state:
    st.session_state.records = []
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

# 매일 다른 질문을 제공하는 함수 (날짜 기반 순환 + 수동 변경 가능)
DAILY_QUESTIONS = [
    "오늘 가장 기억에 남는 따뜻한 순간은 언제였나요?",
    "사랑하는 가족들에게 꼭 들려주고 싶은 어린 시절의 추억이 있나요?",
    "인생에서 가장 행복했던 여행지와 그곳의 공기를 기억하시나요?",
    "힘들 때마다 나를 위로해주었던 말이나 노래가 있다면 무엇인가요?",
    "유족들이 나를 떠올릴 때 어떤 모습으로 기억해주길 바라나요?",
    "함께 식사하며 웃었던 날 중 가장 그리운 날은 언제인가요?",
    "비 오는 날 창밖을 보며 떠올리는 소중한 사람이 있나요?"
]

if "question_offset" not in st.session_state:
    st.session_state.question_offset = 0

def get_today_question():
    day_index = (datetime.now().timetuple().tm_yday + st.session_state.question_offset) % len(DAILY_QUESTIONS)
    return DAILY_QUESTIONS[day_index]

# ==========================================
# 1단계: 회원가입 및 로그인 화면
# ==========================================
if not st.session_state.logged_in:
    st.title("🌿 향기와 목소리")
    st.caption("생전의 따뜻한 목소리와 당신만의 고유한 체취를 사랑하는 사람들에게 남깁니다.")
    st.markdown("---")

    tab_login, tab_signup = st.tabs(["🔑 로그인", "📝 회원가입"])

    with tab_login:
        with st.form("login_form"):
            user_id = st.text_input("아이디", placeholder="테스트 아이디: user1")
            user_pw = st.text_input("비밀번호", type="password", placeholder="테스트 비밀번호: 123")
            submit_login = st.form_submit_button("로그인", use_container_width=True)

            if submit_login:
                if user_id in st.session_state.users and st.session_state.users[user_id]["password"] == user_pw:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_id
                    st.success("로그인되었습니다!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

    with tab_signup:
        with st.form("signup_form"):
            new_id = st.text_input("사용할 아이디")
            new_pw = st.text_input("비밀번호", type="password")
            new_pw_confirm = st.text_input("비밀번호 확인", type="password")
            new_name = st.text_input("성함")
            submit_signup = st.form_submit_button("회원가입 완료", use_container_width=True)

            if submit_signup:
                if not new_id or not new_pw or not new_name:
                    st.warning("모든 항목을 입력해주세요.")
                elif new_id in st.session_state.users:
                    st.error("이미 존재하는 아이디입니다.")
                elif new_pw != new_pw_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.session_state.users[new_id] = {
                        "password": new_pw,
                        "name": new_name,
                        "birth": date(1990, 1, 1),
                        "interests": "",
                        "perfume": "",
                        "softener": "",
                        "family_scent": ""
                    }
                    st.success("회원가입이 완료되었습니다. 로그인 탭에서 로그인해주세요.")

# ==========================================
# 로그인 이후 화면 구성 (2, 3, 4단계 네비게이션)
# ==========================================
else:
    user_info = st.session_state.users[st.session_state.current_user]

    # 사이드바 메뉴 (기획 순서대로 배치)
    st.sidebar.title(f"🌿 {user_info['name']}님의 공간")
    menu = st.sidebar.radio(
        "단계별 메뉴 이동",
        [
            "1. 메인 보드 (음성 녹음 & 기억의 향)",
            "2. 프로필 (나의 체취 저장)",
            "3. 맞춤 향 추천 (유족 전달 리포트)"
        ]
    )
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ==========================================
    # 2단계: 메인 보드 (매일 다른 질문 + 음성 자동 저장 + 기억의 향 입력)
    # ==========================================
    if menu == "1. 메인 보드 (음성 녹음 & 기억의 향)":
        st.title("🎙️ 오늘의 기억 남기기")
        st.write("매일 새로운 질문에 목소리로 답하고, 그 기억이 떠올리는 향기를 적어주세요.")

        # 오늘의 질문 영역
        col_q1, col_q2 = st.columns([0.8, 0.2])
        with col_q1:
            st.subheader("💌 오늘의 질문")
        with col_q2:
            if st.button("🔄 다른 질문"):
                st.session_state.question_offset += 1
                st.rerun()

        today_q = get_today_question()
        st.markdown(f"""
        <div class="question-box">
            <h4 style="margin:0; color:#e65100;">Q. {today_q}</h4>
        </div>
        """, unsafe_allow_html=True)

        # 음성 녹음 위젯 (Streamlit 내장 st.audio_input 사용 -> 녹음 완료 시 즉시 자동 저장)
        st.markdown("##### 1️⃣ 음성 녹음 (녹음을 멈추면 자동으로 저장됩니다)")
        audio_value = st.audio_input("마이크 버튼을 눌러 답변을 녹음하세요")

        if audio_value is not None:
            audio_bytes = audio_value.getvalue()
            current_hash = hashlib.md5(audio_bytes).hexdigest()

            # 새로운 녹음일 경우 자동으로 기록 리스트에 저장
            if current_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = current_hash
                st.session_state.records.append({
                    "id": current_hash[:8],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "question": today_q,
                    "audio_bytes": audio_bytes,
                    "scent_sentence": ""
                })
                st.toast("✅ 음성이 자동으로 안전하게 저장되었습니다!", icon="🎙️")

        # 가장 최근 녹음에 대한 '기억이 불러일으키는 향' 문장 입력
        if st.session_state.records:
            latest_record = st.session_state.records[-1]
            st.markdown("---")
            st.markdown("##### 2️⃣ 이 기억이 불러일으키는 향기 기록하기")
            st.info(f"방금 녹음한 질문: **{latest_record['question']}**")

            with st.form("scent_sentence_form"):
                scent_desc = st.text_input(
                    "이 기억을 떠올리면 어떤 향기가 나나요? 간단한 문장으로 적어주세요.",
                    value=latest_record["scent_sentence"],
                    placeholder="예: 비 온 뒤 젖은 소나무 숲을 걷던 시원하고 차분한 나무 향기"
                )
                save_scent_btn = st.form_submit_button("🌿 기억의 향 저장하기", use_container_width=True)
                if save_scent_btn:
                    if scent_desc.strip():
                        st.session_state.records[-1]["scent_sentence"] = scent_desc.strip()
                        st.success("기억의 향 문장이 저장되었습니다! '3. 맞춤 향 추천' 메뉴에서 분석 결과를 확인할 수 있습니다.")
                    else:
                        st.warning("향을 묘사하는 문장을 입력해주세요.")

        # 저장된 음성 및 향 기록 목록
        st.markdown("---")
        st.subheader(f"📚 보존된 기억 목록 ({len(st.session_state.records)}개)")
        if not st.session_state.records:
            st.caption("아직 녹음된 기록이 없습니다. 위 마이크 버튼을 눌러 첫 번째 목소리를 남겨보세요.")
        else:
            for idx, rec in enumerate(reversed(st.session_state.records)):
                with st.expander(f"[{rec['date']}] {rec['question']}", expanded=(idx == 0)):
                    st.audio(rec["audio_bytes"], format="audio/wav")
                    if rec["scent_sentence"]:
                        st.markdown(f"**🌸 기억의 향:** {rec['scent_sentence']}")
                    else:
                        st.caption("⚠️ 아직 이 기억의 향기가 작성되지 않았습니다.")

    # ==========================================
    # 3단계: 프로필 보드 (체취 저장 기능 및 기본 정보)
    # ==========================================
    elif menu == "2. 프로필 (나의 체취 저장)":
        st.title("🧴 나의 프로필 및 체취 기록")
        st.write("사랑하는 사람들이 기억할 당신의 기본 정보와 고유한 체취를 기록해 주세요.")

        with st.form("profile_form"):
            st.subheader("👤 기본 정보")
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input("이름", value=user_info["name"])
            with col2:
                p_birth = st.date_input("생년월일", value=user_info["birth"], min_value=date(1920, 1, 1), max_value=date.today())
            
            p_interests = st.text_input("평소 관심사 및 취미", value=user_info["interests"], placeholder="예: 가드닝, 클래식 감상, 등산")

            st.markdown("---")
            st.subheader("✨ 나의 체취 저장하기")
            p_perfume = st.text_input(
                "평소 자주 쓰는 향수",
                value=user_info["perfume"],
                placeholder="예: 조말론 우드세이지 앤 씨솔트, 이솝 테싯 등"
            )
            p_softener = st.text_input(
                "평소 사용하는 섬유유연제 / 바디제품",
                value=user_info["softener"],
                placeholder="예: 다우니 어도러블, 르라보 히노키 바디크림 등"
            )
            p_family_scent = st.text_area(
                "가족들이나 사랑하는 사람이 맡는 '나의 향'은 어떤 향인가요?",
                value=user_info["family_scent"],
                placeholder="예: 엄마 품에서 나던 포근한 비누 냄새와 은은한 베이비파우더 향, 혹은 아빠 서재의 오래된 책과 커피 향"
            )

            save_profile = st.form_submit_button("💾 프로필 및 체취 저장하기", use_container_width=True)
            if save_profile:
                st.session_state.users[st.session_state.current_user].update({
                    "name": p_name,
                    "birth": p_birth,
                    "interests": p_interests,
                    "perfume": p_perfume,
                    "softener": p_softener,
                    "family_scent": p_family_scent
                })
                st.success("프로필과 체취 정보가 성공적으로 저장되었습니다!")

    # ==========================================
    # 4단계: 맞춤 향 추천 화면 (음성 기록 + 기억 문장 + 체취 기반 분석)
    # ==========================================
    elif menu == "3. 맞춤 향 추천 (유족 전달 리포트)":
        st.title("💐 유족을 위한 맞춤 향기 리포트")
        st.write(f"**{user_info['name']}**님이 생전에 남긴 목소리와 기억의 문장, 그리고 체취 기록을 종합하여 고인을 추억할 수 있는 시그니처 향을 분석합니다.")

        # 1. 생전의 체취 요약 카드
        st.markdown("### 1️⃣ 생전에 머물던 나의 체취")
        st.markdown(f"""
        <div class="main-card">
            <p><strong>🧴 자주 쓰던 향수:</strong> {user_info['perfume'] or '미입력'}</p>
            <p><strong>🧺 익숙한 섬유유연제:</strong> {user_info['softener'] or '미입력'}</p>
            <p><strong>🤍 사랑하는 이들이 기억하는 체취:</strong><br>{user_info['family_scent'] or '미입력'}</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. 기억 속 향기 문장 분석 로직
        st.markdown("### 2️⃣ 기억의 조각들이 모여 완성된 향 분석")
        scent_sentences = [r["scent_sentence"] for r in st.session_state.records if r["scent_sentence"].strip()]
        
        # 프로필의 가족 체취 문장도 분석에 함께 반영
        all_text = " ".join(scent_sentences) + " " + user_info["family_scent"] + " " + user_info["perfume"]

        if not scent_sentences and not user_info["family_scent"].strip():
            st.warning("아직 분석할 향기 문장이 충분하지 않습니다. 메인 보드에서 음성 녹음 후 기억의 향을 작성하거나, 프로필에 체취를 입력해주세요.")
        else:
            # 키워드 기반 향조(Note) 스코어링 엔진
            note_profiles = {
                "우디 & 어시 (Woody & Earthy)": {
                    "keywords": ["나무", "숲", "소나무", "흙", "비", "책", "서재", "이솝", "히노키", "우드", "차분", "오래된"],
                    "desc": "비 온 뒤 젖은 숲과 오래된 나무처럼 든든하고 변치 않는 위로의 향기",
                    "perfumes": ["이솝 테싯 (Aesop Tacit)", "르라보 상탈 33 (Le Labo Santal 33)", "탐다오 오 드 퍼퓸 (Diptyque Tam Dao)"]
                },
                "플로럴 & 파우더리 (Floral & Powdery)": {
                    "keywords": ["꽃", "비누", "포근", "엄마", "햇살", "빨래", "유연제", "릴리", "장미", "파우더", "따뜻", "봄"],
                    "desc": "햇살 잘 드는 오후의 깨끗한 이불과 포근한 품을 닮은 다정한 향기",
                    "perfumes": ["바이레도 블랑쉬 (Byredo Blanche)", "산타마리아노벨라 프리지아", "딥티크 플레르 드 뽀"]
                },
                "시트러스 & 그린 (Citrus & Green)": {
                    "keywords": ["시원", "풀", "바다", "바람", "레몬", "귤", "오렌지", "여름", "산책", "청량", "아침", "이슬"],
                    "desc": "싱그러운 아침 산책길의 풀잎과 맑은 바람처럼 생동감 넘치는 기억의 향기",
                    "perfumes": ["조말론 우드세이지 앤 씨솔트", "아쿠아 디 파르마 미르토", "에르메스 운 자르뎅 수르닐"]
                },
                "웜 & 스파이시 / 구르망 (Warm & Cozy)": {
                    "keywords": ["커피", "차", "달콤", "바닐라", "겨울", "난로", "빵", "고소", "음식", "저녁", "노을"],
                    "desc": "함께 마주 앉아 나누던 따뜻한 차와 다정한 대화의 온기를 담은 향기",
                    "perfumes": ["메종 마르지엘라 바이 더 파이어플레이스", "조말론 잉글리쉬 페어 앤 프리지아", "딥티크 오 듀엘르"]
                }
            }

            scores = {}
            for category, data in note_profiles.items():
                score = sum(1 for kw in data["keywords"] if kw in all_text)
                scores[category] = score

            # 가장 높은 점수의 향조 선택 (기본값: 우디 & 어시)
            best_category = max(scores, key=scores.get)
            if scores[best_category] == 0:
                best_category = "플로럴 & 파우더리 (Floral & Powdery)"

            result = note_profiles[best_category]

            st.success(f"✨ 분석 결과, **{user_info['name']}**님을 가장 닮은 시그니처 향조는 **[{best_category}]** 입니다.")
            
            st.markdown(f"""
            <div class="main-card">
                <h4 style="margin-top:0;">🌿 유족에게 전하는 향기 메시지</h4>
                <p style="font-size:16px;">"{result['desc']}"</p>
                <hr>
                <p><strong>💡 추억을 간직하기 위해 추천하는 조향 / 향수:</strong></p>
                <div>
                    {''.join([f'<span class="scent-badge">{p}</span>' for p in result['perfumes']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 분석에 활용된 기억 문장 모음
            if scent_sentences:
                st.markdown("#### 📝 분석에 반영된 생전의 기억 문장들")
                for idx, s in enumerate(scent_sentences, 1):
                    st.write(f"{idx}. \"{s}\"")
