
import streamlit as st
import pandas as pd

# Title of the application
st.title("일정 트래킹 서비스")

# Default DataFrame to store schedule data
if "schedule_data" not in st.session_state:
    st.session_state["schedule_data"] = pd.DataFrame(columns=["날짜", "이벤트"])

# Form to input date and event
with st.form("schedule_form"):
    date = st.date_input("날짜 선택")
    event = st.text_input("이벤트 설명")
    submitted = st.form_submit_button("일정 추가")

    # Add to DataFrame when form is submitted
    if submitted and event:
        new_data = {"날짜": date, "이벤트": event}
        st.session_state["schedule_data"] = st.session_state["schedule_data"].append(new_data, ignore_index=True)
        st.success("일정이 추가되었습니다.")

# Display saved schedule data in a table format
st.subheader("저장된 일정")
st.table(st.session_state["schedule_data"])

# Reset schedule functionality
if st.button("일정 초기화"):
    st.session_state["schedule_data"] = pd.DataFrame(columns=["날짜", "이벤트"])
    st.success("일정이 초기화되었습니다.")
