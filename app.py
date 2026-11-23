import streamlit as st
from datetime import datetime, date
import hashlib

# 페이지 기본 설정
st.set_page_config(
    page_title="향기와 목소리 · 기억 보존 서비스",
    page_icon="🌿",
    layout="centered"
)

# 감성 테마 스타일 커스터마이징
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700&family=Pretendard:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #faf7f2 0%, #f4efe6 100%);
        color: #2c2a29;
    }

    h1, h2, h3, .serif-title {
        font-family: 'Noto Serif KR', serif;
        color: #262320;
        letter-spacing: -0.02em;
    }

    /* 상단 브랜드 헤더 */
    .brand-banner {
        background: linear-gradient(135deg, #eef3ee 0%, #f9f4eb 100%);
        border: 1px solid #dfd8ca;
        border-radius: 20px;
        padding: 24px 26px;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(44, 42, 41, 0.04);
    }

    .brand-sub {
        color: #6b645c;
        font-size: 0.95rem;
        margin-top: 6px;
        line-height: 1.5;
    }

    /* 오늘의 질문 카드 */
    .question-card {
        background: #ffffff;
        border: 1px solid #ead8c3;
        border-left: 6px solid #d48c46;
        border-radius: 16px;
        padding: 22px 24px;
        margin: 12px 0 20px 0;
        box-shadow: 0 4px 14px rgba(212, 140, 70, 0.08);
    }

    .question-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #c27832;
        margin-bottom: 6px;
    }

    .question-text {
        font-family: 'Noto Serif KR', serif;
        font-size: 1.18rem;
        font-weight: 700;
        color: #262320;
        line-height: 1.55;
        margin: 0;
    }

    /* 일반 정보/리포트 카드 */
    .soft-card {
        background: #ffffff;
        border: 1px solid #e6dfd3;
        border-radius: 18px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(38, 35, 32, 0.04);
    }

    .highlight-card {
        background: linear-gradient(135deg, #f3f7f2 0%, #ffffff 100%);
        border: 1px solid #c9dac7;
        border-radius: 18px;
        padding: 24px;
        margin: 14px 0 20px 0;
        box-shadow: 0 6px 18px rgba(63, 107, 69, 0.07);
    }

    /* 향수 추천 배지 */
    .scent-chip {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background-color: #edf4ec;
        border: 1px solid #c6dac3;
        color: #2f5d34;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 4px 6px 4px 0;
    }

    .memory-quote {
        background-color: #faf7f2;
        border-left: 3px solid #9ab098;
        padding: 10px 14px;
        border-radius: 0 10px 10px 0;
        margin: 6px 0;
        color: #423e3a;
        font-size: 0.94rem;
    }

    /* 버튼 스타일 */
    .stButton > button, .stFormSubmitButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1rem !important;
        border: 1px solid #dcd3c4 !important;
        transition: all 0.18s ease !important;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: #6b8e6e !important;
        transform: translateY(-1px);
    }

    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #f3eee4;
        border-right: 1px solid #e3dacb;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "users" not in st.session_state:
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
if "question_offset" not in st.session_state:
    st.session_state.question_offset = 0

DAILY_QUESTIONS = [
    "오늘 가장 기억에 남는 따뜻한 순간은 언제였나요?",
    "사랑하는 가족들에게 꼭 들려주고 싶은 어린 시절의 추억이 있나요?",
    "인생에서 가장 행복했던 여행지와 그곳의 공기를 기억하시나요?",
    "힘들 때마다 나를 위로해주었던 말이나 노래가 있다면 무엇인가요?",
    "유족들이 나를 떠올릴 때 어떤 모습으로 기억해주길 바라나요?",
    "함께 식사하며 웃었던 날 중 가장 그리운 날은 언제인가요?",
    "비 오는 날 창밖을 보며 떠올리는 소중한 사람이 있나요?"
]

def get_today_question():
    day_index = (datetime.now().timetuple().tm_yday + st.session_state.question_offset) % len(DAILY_QUESTIONS)
    return DAILY_QUESTIONS[day_index]

# ==========================================
# 1단계: 회원가입 및 로그인 화면
# ==========================================
if not st.session_state.logged_in:
    st.markdown("""
        <div class="brand-banner">
            <h1 style="margin:0;">🌿 향기와 목소리</h1>
            <div class="brand-sub">
                시간이 흘러도 바래지 않는 생전의 따뜻한 목소리와 고유한 체취의 기억을<br>
                가장 사랑하는 사람들에게 온전히 전합니다.
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 로그인", "📝 회원가입"])

    with tab_login:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            user_id = st.text_input("아이디", placeholder="테스트 계정: user1")
            user_pw = st.text_input("비밀번호", type="password", placeholder="테스트 비밀번호: 123")
            submit_login = st.form_submit_button("로그인", use_container_width=True)

            if submit_login:
                if user_id in st.session_state.users and st.session_state.users[user_id]["password"] == user_pw:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_id
                    st.session_state.last_audio_hash = None
                    st.success("환영합니다. 기억의 공간으로 이동합니다.")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호를 다시 확인해주세요.")
        st.caption("💡 빠른 체험을 원하시면 `user1` / `123`으로 로그인해 보세요.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_signup:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        with st.form("signup_form"):
            new_id = st.text_input("사용할 아이디")
            new_name = st.text_input("성함")
            col_pw1, col_pw2 = st.columns(2)
            with col_pw1:
                new_pw = st.text_input("비밀번호", type="password")
            with col_pw2:
                new_pw_confirm = st.text_input("비밀번호 확인", type="password")
            submit_signup = st.form_submit_button("회원가입 완료", use_container_width=True)

            if submit_signup:
                if not new_id or not new_pw or not new_name:
                    st.warning("모든 항목을 입력해주세요.")
                elif new_id in st.session_state.users:
                    st.error("이미 사용 중인 아이디입니다.")
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
                    st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 로그인 이후 화면 (2, 3, 4단계)
# ==========================================
else:
    current_user_id = st.session_state.current_user
    user_info = st.session_state.users[current_user_id]
    user_records = [r for r in st.session_state.records if r.get("owner") == current_user_id]
    scent_count = sum(1 for r in user_records if r.get("scent_sentence", "").strip())

    # 사이드바
    with st.sidebar:
        st.markdown(f"### 🌿 {user_info['name']}님")
        st.caption("소중한 목소리와 향기의 기록")
        st.markdown("---")

        menu = st.radio(
            "메뉴 선택",
            [
                "1. 메인 보드 (음성 녹음 & 기억의 향)",
                "2. 프로필 (나의 체취 저장)",
                "3. 맞춤 향 추천 (유족 전달 리포트)"
            ]
        )

        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("녹음 기록", f"{len(user_records)}개")
        m2.metric("향 문장", f"{scent_count}개")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.last_audio_hash = None
            st.rerun()

    # ==========================================
    # 2단계: 메인 보드
    # ==========================================
    if menu == "1. 메인 보드 (음성 녹음 & 기억의 향)":
        st.markdown("""
            <div class="brand-banner">
                <h1 style="margin:0;">🎙️ 오늘의 기억 남기기</h1>
                <div class="brand-sub">오늘의 질문에 목소리로 답하고, 그 순간 떠오르는 향기를 문장으로 남겨보세요.</div>
            </div>
        """, unsafe_allow_html=True)

        top_l, top_r = st.columns([0.75, 0.25])
        with top_l:
            st.markdown("#### 💌 오늘의 질문")
        with top_r:
            if st.button("🔄 다른 질문", use_container_width=True):
                st.session_state.question_offset += 1
                st.rerun()

        today_q = get_today_question()
        st.markdown(f"""
            <div class="question-card">
                <div class="question-label">DAILY MEMORY PROMPT</div>
                <p class="question-text">“{today_q}”</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("#### 1️⃣ 음성 녹음")
        st.caption("마이크 버튼을 눌러 녹음을 마친 뒤 멈추면 자동으로 저장됩니다.")
        audio_value = st.audio_input("답변을 음성으로 녹음하세요", label_visibility="collapsed")

        if audio_value is not None:
            audio_bytes = audio_value.getvalue()
            current_hash = hashlib.md5(audio_bytes).hexdigest()

            if current_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = current_hash
                st.session_state.records.append({
                    "id": current_hash[:8],
                    "owner": current_user_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "question": today_q,
                    "audio_bytes": audio_bytes,
                    "scent_sentence": ""
                })
                st.toast("✅ 음성이 자동으로 저장되었습니다.", icon="🎙️")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        user_records = [r for r in st.session_state.records if r.get("owner") == current_user_id]

        if user_records:
            latest_record = user_records[-1]
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown("#### 2️⃣ 기억이 불러일으키는 향기")
            st.caption(f"선택된 기록: **{latest_record['question']}**")

            with st.form("scent_sentence_form"):
                scent_desc = st.text_input(
                    "이 기억을 떠올리면 어떤 향기가 나나요? 간단한 문장으로 적어주세요.",
                    value=latest_record["scent_sentence"],
                    placeholder="예: 비 온 뒤 젖은 소나무 숲을 걷던 시원하고 차분한 나무 향기"
                )
                save_scent_btn = st.form_submit_button("🌿 기억의 향 저장하기", use_container_width=True)
                if save_scent_btn:
                    if scent_desc.strip():
                        for rec in st.session_state.records:
                            if rec["id"] == latest_record["id"] and rec.get("owner") == current_user_id:
                                rec["scent_sentence"] = scent_desc.strip()
                                break
                        st.success("기억의 향 문장이 저장되었습니다.")
                        st.rerun()
                    else:
                        st.warning("향을 묘사하는 문장을 입력해주세요.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"#### 📚 보존된 기억 아카이브 ({len(user_records)}개)")
        if not user_records:
            st.markdown("""
                <div class="soft-card" style="text-align:center; color:#756e65;">
                    아직 남겨진 목소리가 없습니다. 위에서 첫 번째 기억을 녹음해 보세요.
                </div>
            """, unsafe_allow_html=True)
        else:
            for idx, rec in enumerate(reversed(user_records)):
                with st.expander(f"🕊️ {rec['date']}  ·  {rec['question']}", expanded=(idx == 0)):
                    st.audio(rec["audio_bytes"], format="audio/wav")
                    if rec["scent_sentence"]:
                        st.markdown(f'<div class="memory-quote">🌸 <strong>기억의 향:</strong> {rec["scent_sentence"]}</div>', unsafe_allow_html=True)
                    else:
                        st.caption("아직 이 기억의 향기 문장이 작성되지 않았습니다.")

    # ==========================================
    # 3단계: 프로필 보드
    # ==========================================
    elif menu == "2. 프로필 (나의 체취 저장)":
        st.markdown("""
            <div class="brand-banner">
                <h1 style="margin:0;">🧴 나의 프로필 및 체취</h1>
                <div class="brand-sub">소중한 사람들이 기억할 당신의 기본 정보와 일상의 체취를 기록합니다.</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        with st.form("profile_form"):
            st.markdown("#### 👤 기본 정보")
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input("이름", value=user_info["name"])
            with c2:
                p_birth = st.date_input(
                    "생년월일",
                    value=user_info["birth"],
                    min_value=date(1920, 1, 1),
                    max_value=date.today()
                )
            p_interests = st.text_input(
                "관심사 및 취미",
                value=user_info["interests"],
                placeholder="예: 산책, 독서, 클래식 음악, 정원 가꾸기"
            )

            st.markdown("---")
            st.markdown("#### ✨ 나의 체취 기록")
            p_perfume = st.text_input(
                "평소 자주 쓰는 향수",
                value=user_info["perfume"],
                placeholder="예: 이솝 테싯, 조말론 우드세이지 앤 씨솔트"
            )
            p_softener = st.text_input(
                "평소 사용하는 섬유유연제 / 바디제품",
                value=user_info["softener"],
                placeholder="예: 다우니 화이트티와 릴리, 히노키 바디로션"
            )
            p_family_scent = st.text_area(
                "가족들이나 사랑하는 사람이 맡는 '나의 향'은 어떤 향인가요?",
                value=user_info["family_scent"],
                height=105,
                placeholder="예: 비 온 뒤 젖은 흙냄새와 은은한 나무 향이 섞인 포근한 냄새"
            )

            if st.form_submit_button("💾 프로필 및 체취 저장하기", use_container_width=True):
                st.session_state.users[current_user_id].update({
                    "name": p_name,
                    "birth": p_birth,
                    "interests": p_interests,
                    "perfume": p_perfume,
                    "softener": p_softener,
                    "family_scent": p_family_scent
                })
                st.success("프로필과 체취 정보가 저장되었습니다.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 4단계: 맞춤 향 추천 화면
    # ==========================================
    elif menu == "3. 맞춤 향 추천 (유족 전달 리포트)":
        st.markdown(f"""
            <div class="brand-banner">
                <h1 style="margin:0;">💐 {user_info['name']}님의 향기 리포트</h1>
                <div class="brand-sub">생전의 음성 기록에 담긴 기억 문장과 일상의 체취를 모아 유족에게 전하는 향기 안내입니다.</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="soft-card">
                <h4 style="margin-top:0;">🤍 생전에 머물던 체취</h4>
                <p style="margin:6px 0;"><strong>향수:</strong> {user_info['perfume'] or '기록 없음'}</p>
                <p style="margin:6px 0;"><strong>섬유유연제 · 바디제품:</strong> {user_info['softener'] or '기록 없음'}</p>
                <p style="margin:6px 0;"><strong>가족들이 기억하는 향:</strong> {user_info['family_scent'] or '기록 없음'}</p>
            </div>
        """, unsafe_allow_html=True)

        scent_sentences = [r["scent_sentence"] for r in user_records if r["scent_sentence"].strip()]
        all_text = " ".join(scent_sentences) + " " + user_info["family_scent"] + " " + user_info["perfume"]

        if not scent_sentences and not user_info["family_scent"].strip():
            st.info("아직 분석할 향기 기록이 충분하지 않습니다. 메인 보드에서 기억의 향을 작성하거나 프로필에 체취를 남겨주세요.")
        else:
            note_profiles = {
                "우디 & 어시 (Woody & Earthy)": {
                    "keywords": ["나무", "숲", "소나무", "흙", "비", "책", "서재", "이솝", "히노키", "우드", "차분", "오래된"],
                    "desc": "비 온 뒤 젖은 숲과 오래된 나무처럼 든든하고 변치 않는 위로의 향기",
                    "perfumes": ["이솝 테싯 (Aesop Tacit)", "르라보 상탈 33 (Le Labo Santal 33)", "딥티크 탐다오 (Diptyque Tam Dao)"]
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

            scores = {cat: sum(1 for kw in data["keywords"] if kw in all_text) for cat, data in note_profiles.items()}
            best_category = max(scores, key=scores.get)
            if scores[best_category] == 0:
                best_category = "플로럴 & 파우더리 (Floral & Powdery)"

            result = note_profiles[best_category]
            chips_html = "".join([f'<span class="scent-chip">🌸 {p}</span>' for p in result["perfumes"]])

            st.markdown(f"""
                <div class="highlight-card">
                    <div class="question-label">SIGNATURE SCENT RECOMMENDATION</div>
                    <h3 style="margin:4px 0 12px 0;">{best_category}</h3>
                    <p style="font-size:1.02rem; line-height:1.6; color:#36332f;">“{result['desc']}”</p>
                    <hr style="border:none; border-top:1px solid #d5e2d3; margin:16px 0;">
                    <div style="font-size:0.9rem; font-weight:600; color:#2f5d34; margin-bottom:8px;">추천 향수 · 향조 레퍼런스</div>
                    <div>{chips_html}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📊 향조별 키워드 반응 분포")
            total_score = sum(scores.values())
            for cat, sc in scores.items():
                ratio = (sc / total_score) if total_score > 0 else 0.0
                c_label, c_bar = st.columns([0.42, 0.58])
                with c_label:
                    st.write(f"**{cat.split(' (')[0]}** ({sc}점)")
                with c_bar:
                    st.progress(min(max(ratio, 0.0), 1.0))

            if scent_sentences:
                st.markdown("#### 📝 분석에 반영된 기억 문장")
                for s in scent_sentences:
                    st.markdown(f'<div class="memory-quote">“{s}”</div>', unsafe_allow_html=True)
