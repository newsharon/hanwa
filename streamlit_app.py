import streamlit as st
from dataset import create_fake_merged
from recommendation import get_top_customers_by_role
import pandas as pd
import time
import pyperclip

# 한화생명 브랜드 컬러
HANHWA_ORANGE = "#FF7100"
HANHWA_DEEP_ORANGE = "#FF9600"
HANHWA_LIGHT_ORANGE = "#FFF3E0"
HANHWA_GRAY = "#F5F5F5"
HANHWA_FONT = "Pretendard, Noto Sans KR, sans-serif"

# LLM API 호출 흉내 함수 (실제 연동 시 이 부분만 교체)
def call_llm_api(prompt: str):
    time.sleep(0.5)
    return [
        "고객님, 최근 접점과 이벤트를 바탕으로 맞춤 안내를 드립니다. 궁금한 점 있으시면 언제든 문의주세요.",
        "고객님, 주요 이벤트가 확인되어 안내드립니다. 건강과 행복을 기원합니다.",
        "고객님, 항상 저희 서비스를 이용해주셔서 감사합니다. 필요한 사항이 있으시면 언제든 연락주세요."
    ]

def build_messages(customer, 목적="가입유도", report_summary=None, events=None, history=None):
    name = customer.get('POLR_CUST_ID', '고객님')
    recent = customer.get('RFDT', '')
    channel = customer.get('채널구분', '')
    bswr = customer.get('BSWR_NM', '')
    event_str = ", ".join(events) if events else "없음"
    목적_문구 = "가입을 추천드립니다" if 목적 == "가입유도" else "이탈 방지를 위해 도움을 드리고자 합니다"
    prompt = f"{name}님, 최근 {recent.date()}에 {channel} 채널을 통해 {bswr} 업무를 이용해주셔서 감사합니다. {event_str} 이벤트가 있어 {목적_문구}."
    return call_llm_api(prompt)

def copy_to_clipboard(text):
    pyperclip.copy(text)
    st.toast("메시지가 복사되었습니다!", icon="✅")

st.set_page_config(page_title="FP 고객 추천 서비스", layout="wide", initial_sidebar_state="auto")

# 헤더
st.markdown(f'''
<div style="width:100%;background:#fff;border-bottom:2px solid {HANHWA_ORANGE};padding:12px 0 8px 0;position:sticky;top:0;z-index:100;">
  <div style="display:flex;align-items:center;max-width:1100px;margin:0 auto;">
    <div style="width:40px;height:40px;background:{HANHWA_ORANGE};border-radius:8px;display:flex;align-items:center;justify-content:center;margin-right:14px;">
      <span style="color:white;font-weight:bold;font-size:1.2rem;">H</span>
    </div>
    <span style="font-size:1.35rem;font-weight:700;color:{HANHWA_ORANGE};letter-spacing:1px;">FP 고객 추천 서비스</span>
  </div>
</div>
''', unsafe_allow_html=True)

# (서비스 안내/개인정보 보호 안내 expander 제거)

# 스타일
st.markdown(f"""
<style>
body, .stApp {{ font-family: {HANHWA_FONT}; }}
.card {{
  border: 1.5px solid {HANHWA_ORANGE};
  border-radius: 16px;
  background: {HANHWA_LIGHT_ORANGE};
  padding: 22px 20px 14px 20px;
  margin-bottom: 22px;
  box-shadow: 0 2px 12px 0 #ff710033;
  transition: box-shadow 0.2s, background 0.2s;
}}
.card:hover {{
  box-shadow: 0 4px 18px 0 #ff710066;
  background: #fff7ed;
}}
.card-title {{
  font-size: 1.15rem;
  font-weight: bold;
  margin-bottom: 7px;
  color: {HANHWA_ORANGE};
  letter-spacing: 0.5px;
}}
.card-sub {{
  color: #888;
  font-size: 0.97rem;
  margin-bottom: 10px;
}}
.badge {{
  background: {HANHWA_DEEP_ORANGE};
  color: white;
  padding: 2px 12px;
  border-radius: 10px;
  font-size: 0.92em;
  margin-left: 8px;
}}
.metric-orange .stMetricDeltaPositive {{ color: {HANHWA_ORANGE} !important; }}
.stTabs [data-baseweb="tab"] {{ font-size:1.1rem; font-weight:600; color:{HANHWA_ORANGE}; }}
.stButton>button {{ background:{HANHWA_ORANGE}; color:white; border-radius:8px; border:none; font-weight:600; }}
.stButton>button:hover {{ background:{HANHWA_DEEP_ORANGE}; }}
.copy-btn {{ background:#fff;border:1.2px solid {HANHWA_ORANGE};color:{HANHWA_ORANGE};border-radius:7px;padding:2px 12px;font-size:0.98em;cursor:pointer;margin-left:8px; }}
.copy-btn:hover {{ background:{HANHWA_ORANGE};color:#fff; }}
</style>
""", unsafe_allow_html=True)

st.markdown("### 📋 FP 담당자님, 고객 추천을 위해 ID를 입력해주세요")
st.markdown("고객 데이터를 분석하여 가입 유도 및 이탈 방지가 필요한 고객을 추천해드립니다.")

fp_id = st.text_input(
    "담당자 ID", 
    "F001",
    placeholder="예: F001, F002, F003...",
    help="담당하시는 FP ID를 입력하시면 해당하는 고객 리스트를 분석해드립니다."
)

if st.button("고객 추천 보기"):
    merged = create_fake_merged(50)
    top5_join, top5_leave = get_top_customers_by_role(fp_id, merged)
    st.session_state['merged'] = merged
    st.session_state['top5_join'] = top5_join
    st.session_state['top5_leave'] = top5_leave
    for idx in range(5):
        st.session_state[f'join_msg_{idx}_clicked'] = False
        st.session_state[f'leave_msg_{idx}_clicked'] = False

# FP용 전문 리포트 생성 함수
def make_fp_report(customer, events, history, purpose):
    event_badges = "<span style='color:#888;'>특이 이벤트 없음</span>"
    if events:
        event_badges = " ".join([
            f"<span style='display:inline-block;background:#FF9600;color:#fff;padding:2px 10px;border-radius:8px;margin:2px 4px 2px 0;font-size:0.97em;'>{e.replace('여부','')}</span>"
            for e in events
        ])
    recent = customer.get('RFDT', '')
    channel = customer.get('채널구분', '')
    work = customer.get('업무구분', '')
    bswr = customer.get('BSWR_NM', '')
    join_rate = customer.get('터치_가입률', 0)
    base_rate = customer.get('미터치_가입률', 0)
    leave_diff = customer.get('이탈률_차이', 0)
    prev_str = "최근 접점 내역 없음"
    prev_list_html = ""
    if history is not None:
        if hasattr(history, 'empty'):
            if not history.empty:
                prev = [f"{h['RFDT'].date()} ({h['채널구분']}/{h['업무구분']})" for _, h in history.iterrows()][:5]
                prev_str = ", ".join(prev)
                prev_list_html = "<ul style='margin:4px 0 0 12px;padding:0;'>" + "".join([f"<li style='color:#333;font-size:0.97em;'>{item}</li>" for item in prev]) + "</ul>"
        elif isinstance(history, list) and len(history) > 0:
            prev = [f"{h['RFDT'].date()} ({h['채널구분']}/{h['업무구분']})" for h in history[:5]]
            prev_str = ", ".join(prev)
            prev_list_html = "<ul style='margin:4px 0 0 12px;padding:0;'>" + "".join([f"<li style='color:#333;font-size:0.97em;'>{item}</li>" for item in prev]) + "</ul>"
    if purpose == "가입유도":
        return f"""
<div style='background:#fff7ed;border-radius:10px;padding:14px 16px 10px 16px;margin-bottom:8px;border-left:5px solid {HANHWA_ORANGE};'>
  <b style='color:{HANHWA_ORANGE};font-size:1.08em;'>[고객 요약]</b><br>
  <span style='color:#333;'>
    - 최근 <b>{recent.date()}</b>에 <b>{channel}</b> 채널을 통해 <b>{work}({bswr})</b> 업무로 접점이 있었습니다.<br>
    - 이번 달 이벤트:<br>{event_badges}<br>
    - 가입률이 <b>{base_rate:.1%}</b>에서 <b>{join_rate:.1%}</b>로 상승할 여지가 있습니다.<br>
    - 최근 접점 내역(최신순):
    {prev_list_html}
  </span>
  <hr style='border:0;border-top:1px dashed #FF9600;margin:10px 0;'>
  <b style='color:{HANHWA_ORANGE};'>[FP 참고]</b><br>
  <span style='color:#222;'>
    - 이벤트 발생 시점에 맞춰 <b>신규 상품/혜택 안내</b>를 권장합니다.<br>
    - 고객의 관심사나 최근 문의 이력도 함께 확인해 주세요.
  </span>
</div>
"""
    else:
        return f"""
<div style='background:#fff7ed;border-radius:10px;padding:14px 16px 10px 16px;margin-bottom:8px;border-left:5px solid {HANHWA_DEEP_ORANGE};'>
  <b style='color:{HANHWA_DEEP_ORANGE};font-size:1.08em;'>[고객 요약]</b><br>
  <span style='color:#333;'>
    - 최근 <b>{recent.date()}</b>에 <b>{channel}</b> 채널로 <b>{work}({bswr})</b> 업무를 진행했습니다.<br>
    - 이번 달 이벤트:<br>{event_badges}<br>
    - 이탈률 차이가 <b>{leave_diff:.2%}</b>로, 이탈 위험이 높아진 상태입니다.<br>
    - 최근 접점 내역(최신순):
    {prev_list_html}
  </span>
  <hr style='border:0;border-top:1px dashed #FF9600;margin:10px 0;'>
  <b style='color:{HANHWA_DEEP_ORANGE};'>[FP 참고]</b><br>
  <span style='color:#222;'>
    - 이탈 위험 고객에게는 <b>맞춤 혜택, 보장 강화, 상담 예약</b> 등을 적극 제안해 주세요.<br>
    - 고객의 불만/문의 이력도 함께 점검 바랍니다.
  </span>
</div>
"""

# 카드/리포트 함수

def make_customer_report(customer, history, purpose):
    events = [k for k in customer.keys() if customer[k] == "Y" and "여부" in k]
    return make_fp_report(customer, events, history, purpose), events

def get_history(df, customer, n=5):
    cust_id = customer['POLR_CUST_ID']
    this_date = customer['RFDT']
    history = df[(df['POLR_CUST_ID'] == cust_id) & (df['RFDT'] < this_date)]
    history = history.sort_values('RFDT', ascending=False).head(n)
    return history

def history_to_list(history):
    return [row for _, row in history.iterrows()]

if 'top5_join' in st.session_state and 'top5_leave' in st.session_state:
    merged = st.session_state['merged']
    top5_join = st.session_state['top5_join']
    top5_leave = st.session_state['top5_leave']

    tab1, tab2 = st.tabs(["✅ 가입 유도 고객", "✅ 이탈 방지 고객"])

    # 카드 컬럼 레이아웃 (2열)
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, c in enumerate(top5_join):
            with cols[idx % 2]:
                with st.container():
                    history = get_history(merged, c, n=5)
                    report, events = make_customer_report(c, history, "가입유도")
                    st.markdown(f"""
                    <div class='card'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <span class='card-title'>🟠 {c['POLR_CUST_ID']} | {c['BSWR_NM']}</span>
                            <span class='badge'>가입유도</span>
                        </div>
                        <div class='card-sub'>
                            <span style='color:{HANHWA_ORANGE};font-weight:600;'>최근 접점일: {c['RFDT'].date()}</span> | 가입률 변화: <b style='color:{HANHWA_DEEP_ORANGE};'>{c['미터치_가입률']:.1%} → {c['터치_가입률']:.1%}</b>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    col1.metric("가입률", f"{c['터치_가입률']:.1%}", f"{c['터치_가입률']-c['미터치_가입률']:+.1%}", delta_color="normal")
                    col2.metric("이탈률 차이", f"{c['이탈률_차이']:.2%}", delta_color="inverse")
                    # 고객 요약 버튼 (key 분리)
                    report_btn_key = f"join_report_btn_{idx}"
                    report_state_key = f"join_report_{idx}_shown"
                    if st.button("고객 요약 보기", key=report_btn_key):
                        st.session_state[report_state_key] = True
                    if st.session_state.get(report_state_key, False):
                        st.markdown(report, unsafe_allow_html=True)
                    with st.expander("상세 정보/원본 데이터 보기"):
                        st.json({k: v for k, v in c.items() if not isinstance(v, float) or not pd.isna(v)})
                    msg_key = f"join_msg_{idx}"
                    msg_state_key = f"join_msg_{idx}_clicked"
                    if st.button("✉️ 메시지 생성", key=msg_key):
                        st.session_state[msg_state_key] = True
                    if st.session_state.get(msg_state_key, False):
                        with st.spinner("AI 메시지 생성 중..."):
                            messages = build_messages(
                                c,
                                목적="가입유도",
                                report_summary=report,
                                events=events,
                                history=history_to_list(history)
                            )
                        st.markdown("**고객 메시지 제안**:")
                        for m in messages:
                            st.info(m)
                            st.button("복사", key=f"copy_join_{idx}_{m}", on_click=copy_to_clipboard, args=(m,), help="메시지 복사")
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, c in enumerate(top5_leave):
            with cols[idx % 2]:
                with st.container():
                    history = get_history(merged, c, n=5)
                    report, events = make_customer_report(c, history, "이탈방지")
                    st.markdown(f"""
                    <div class='card'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <span class='card-title'>🔵 {c['POLR_CUST_ID']} | {c['BSWR_NM']}</span>
                            <span class='badge' style='background:{HANHWA_ORANGE};'>이탈방지</span>
                        </div>
                        <div class='card-sub'>
                            <span style='color:{HANHWA_ORANGE};font-weight:600;'>최근 접점일: {c['RFDT'].date()}</span> | 이탈률 차이: <b style='color:{HANHWA_DEEP_ORANGE};'>{c['이탈률_차이']:.2%}</b>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    col1.metric("가입률", f"{c['터치_가입률']:.1%}", f"{c['터치_가입률']-c['미터치_가입률']:+.1%}", delta_color="normal")
                    col2.metric("이탈률 차이", f"{c['이탈률_차이']:.2%}", delta_color="inverse")
                    # 고객 요약 버튼 (key 분리)
                    report_btn_key = f"leave_report_btn_{idx}"
                    report_state_key = f"leave_report_{idx}_shown"
                    if st.button("고객 요약 보기", key=report_btn_key):
                        st.session_state[report_state_key] = True
                    if st.session_state.get(report_state_key, False):
                        st.markdown(report, unsafe_allow_html=True)
                    with st.expander("상세 정보/원본 데이터 보기"):
                        st.json({k: v for k, v in c.items() if not isinstance(v, float) or not pd.isna(v)})
                    msg_key = f"leave_msg_{idx}"
                    msg_state_key = f"leave_msg_{idx}_clicked"
                    if st.button("✉️ 메시지 생성", key=msg_key):
                        st.session_state[msg_state_key] = True
                    if st.session_state.get(msg_state_key, False):
                        with st.spinner("AI 메시지 생성 중..."):
                            messages = build_messages(
                                c,
                                목적="이탈방지",
                                report_summary=report,
                                events=events,
                                history=history_to_list(history)
                            )
                        st.markdown("**고객 메시지 제안**:")
                        for m in messages:
                            st.info(m)
                            st.button("복사", key=f"copy_leave_{idx}_{m}", on_click=copy_to_clipboard, args=(m,), help="메시지 복사")
                    st.markdown("</div>", unsafe_allow_html=True) 