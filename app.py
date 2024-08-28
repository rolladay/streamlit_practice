import streamlit as st
import time

# 게임 타이틀
st.title("타이핑 속도 측정 게임")

# 타이핑 테스트에 사용할 문장
test_sentence = "이 문장을 가능한 빨리 타이핑하세요!"

# 게임 시작을 위한 버튼
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if st.button("게임 시작"):
    st.session_state.start_time = time.time()  # 현재 시간을 저장하여 게임 시작 시간으로 사용
    st.session_state.user_input = ""  # 입력 필드 초기화

# 사용자가 타이핑할 문장을 표시
st.write(f"타이핑할 문장: {test_sentence}")

# 타이핑 입력 필드
user_input = st.text_input("입력 필드", st.session_state.user_input)

# 사용자가 입력하는 동안 입력 필드를 업데이트
st.session_state.user_input = user_input

# 사용자가 입력을 완료했는지 확인
if user_input == test_sentence and st.session_state.start_time is not None:
    end_time = time.time()  # 현재 시간을 저장하여 게임 종료 시간으로 사용
    time_taken = end_time - st.session_state.start_time  # 걸린 시간 계산
    st.write(f"축하합니다! 완료하는 데 걸린 시간: {time_taken:.2f} 초")
    st.session_state.start_time = None  # 게임 초기화
else:
    st.write("올바른 문장을 입력하세요!")
