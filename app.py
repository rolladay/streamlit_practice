import streamlit as st
import pandas as pd

# 애플리케이션 제목
st.title("일정 트래킹 서비스")

# 데이터 저장을 위한 기본 DataFrame 설정
if "schedule_data" not in st.session_state:
    st.session_state["schedule_data"] = pd.DataFrame(columns=["날짜", "이벤트"])

# 날짜와 이벤트 입력을 위한 폼 생성
with st.form("schedule_form"):
    date = st.date_input("날짜 선택")
    event = st.text_input("이벤트 설명")
    submitted = st.form_submit_button("일정 추가")

    # 폼이 제출되었을 때 DataFrame에 추가
    if submitted and event:
        new_data = {"날짜": date, "이벤트": event}
        
        # 기존 DataFrame을 복사하고 업데이트
        schedule_data = st.session_state["schedule_data"].copy()
        schedule_data = pd.concat([schedule_data, pd.DataFrame([new_data])], ignore_index=True)
        
        # 업데이트된 DataFrame을 세션 상태에 저장
        st.session_state["schedule_data"] = schedule_data
        
        st.success("일정이 추가되었습니다.")

# 저장된 일정 데이터를 테이블 형식으로 표시
st.subheader("저장된 일정")
st.table(st.session_state["schedule_data"])

# 일정 초기화 기능
if st.button("일정 초기화"):
    st.session_state["schedule_data"] = pd.DataFrame(columns=["날짜", "이벤트"])
    st.success("일정이 초기화되었습니다.")
