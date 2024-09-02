import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import openai
import yfinance as yf
import requests

# OpenAI API 키 설정
openai.api_key = "sk-iv2lZR-RmhJr3VeLYdPeT6yS-d--k1CcZKa5oGx6BwT3BlbkFJArWx9xkyLIIMuXo9ZNe4RHPQK07QmfsId0lMvBOskA"

# 데이터베이스 연결 설정 (SQLite 사용)
engine = create_engine('sqlite:///company_info.db')

# 데이터베이스 초기화 함수 (앱 시작 시 한 번만 실행)
@st.cache_resource
def init_db():
    with engine.connect() as conn:
        # 테이블이 존재하지 않으면 생성
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            market_cap TEXT,
            sector TEXT,
            industry TEXT,
            employees INTEGER,
            website TEXT,
            telecom_collaboration TEXT,
            ai_datacenter_trends TEXT
        )
        """))
        
        # partnerships 열이 존재하지 않으면 추가
        try:
            conn.execute(text("ALTER TABLE companies ADD COLUMN partnerships TEXT"))
        except Exception as e:
            print(f"Column 'partnerships' might already exist: {e}")

# OpenAI API를 사용하여 기업 개요 및 추가 정보 가져오기
def get_company_info(company_name):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "한국어로 상세한 기업 정보를 제공하는 도우미입니다."},
            {"role": "user", "content": f"""
            {company_name} 기업에 대해 다음 정보를 제공해주세요:
            1. 기업 개요
            2. Telecom 기업과의 협력 가능성에 대한 예시 3가지
            3. AI 및 데이터센터 관련 사업동향 및 파트너 관계
            각 항목을 구분하여 답변해주세요.
            """}
        ]
    )
    full_response = response['choices'][0]['message']['content'].strip()
    
    # 응답을 섹션별로 분리
    sections = full_response.split('\n\n')
    overview = sections[0] if len(sections) > 0 else "정보 없음"
    telecom_collaboration = sections[1] if len(sections) > 1 else "정보 없음"
    ai_datacenter_trends = sections[2] if len(sections) > 2 else "정보 없음"
    
    return overview, telecom_collaboration, ai_datacenter_trends

# 기업명으로 티커 심볼 찾기 (개선된 버전)
def get_ticker_from_name(company_name):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'quotes' in data and len(data['quotes']) > 0:
        return data['quotes'][0]['symbol']
    return None

# Yahoo Finance를 사용하여 재무 정보 가져오기
def get_financial_info(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        market_cap = info.get('marketCap', None)
        if market_cap:
            market_cap = f"{market_cap:,} USD"
        else:
            market_cap = "정보 없음"
        
        return {
            'name': info.get('longName', '정보 없음'),
            'market_cap': market_cap,
            'sector': info.get('sector', '정보 없음'),
            'industry': info.get('industry', '정보 없음'),
            'employees': info.get('fullTimeEmployees', '정보 없음'),
            'website': info.get('website', '정보 없음')
        }
    except Exception as e:
        st.error(f"재무 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# 매출 및 영업이익 데이터 가져오기 (개선된 버전)
def get_financial_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        financials = ticker.financials
        
        if financials.empty:
            return None

        revenue = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else None
        operating_income = financials.loc['Operating Income'] if 'Operating Income' in financials.index else None

        if revenue is None or operating_income is None:
            return None

        years = min(3, len(revenue))
        df = pd.DataFrame({
            '매출': revenue.iloc[:years],
            '영업이익': operating_income.iloc[:years]
        })
        return df
    except Exception as e:
        st.error(f"재무 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# OpenAI API를 사용하여 제휴 관계에 있는 회사 찾기
def get_partnerships(company_name):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "한국어로 기업의 제휴 관계를 분석하는 도우미입니다."},
            {"role": "user", "content": f"{company_name}와 협력하거나 투자 관계에 있는 회사들을 알려주세요."}
        ]
    )
    partnerships = response['choices'][0]['message']['content'].strip()
    return partnerships

# Streamlit 앱 설정
st.title("한눈에 살펴보는 기업정보")

# DB 초기화
init_db()

# 사용자로부터 기업명 입력 받기
company_name = st.text_input("기업명을 영어로 입력하세요 (예: softbank, Apple, Samsung):")

if company_name:
    ticker_symbol = get_ticker_from_name(company_name)
    
    if ticker_symbol:
        st.write(f"검색된 티커 심볼: {ticker_symbol}")
        
        financial_info = get_financial_info(ticker_symbol)
        
        if financial_info:
            overview, telecom_collaboration, ai_datacenter_trends = get_company_info(financial_info['name'])
            partnerships = get_partnerships(financial_info['name'])
            
            with engine.connect() as conn:
                conn.execute(text("""
                INSERT OR REPLACE INTO companies 
                (ticker, name, description, market_cap, sector, industry, employees, website, telecom_collaboration, ai_datacenter_trends, partnerships) 
                VALUES (:ticker, :name, :description, :market_cap, :sector, :industry, :employees, :website, :telecom_collaboration, :ai_datacenter_trends, :partnerships)
                """), {
                    'ticker': ticker_symbol,
                    'name': financial_info['name'],
                    'description': overview,
                    'market_cap': financial_info['market_cap'],
                    'sector': financial_info['sector'],
                    'industry': financial_info['industry'],
                    'employees': financial_info['employees'],
                    'website': financial_info['website'],
                    'telecom_collaboration': telecom_collaboration,
                    'ai_datacenter_trends': ai_datacenter_trends,
                    'partnerships': partnerships
                })
            
            st.write(f"## {financial_info['name']} ({ticker_symbol}) 정보")
            
            df = pd.DataFrame([financial_info])
            st.table(df.T)
            
            st.write("### 기업 개요")
            st.write(overview)
            
            st.write("### Telecom 컴패니와 협력 가능성")
            st.write(telecom_collaboration)
            
            st.write("### AI 및 데이터센터 관련 사업동향 및 파트너 관계")
            st.write(ai_datacenter_trends)
            
            st.write("### 제휴 관계에 있는 회사들")
            st.write(partnerships)
            
            # 주가 차트 기간 선택 옵션 추가
            chart_period = st.selectbox("주가 차트 기간 선택:", ["1년", "3년", "5년"])
            period_map = {"1년": "1y", "3년": "3y", "5년": "5y"}
            period = period_map[chart_period]

            st.write(f"### 주가 차트 (최근 {chart_period})")
            stock_data = yf.download(ticker_symbol, period=period)
            st.line_chart(stock_data['Close'])
            
            # 매출과 영업이익 테이블 추가
            st.write("### 매출 및 영업이익 (최근 3개년)")
            financial_data = get_financial_data(ticker_symbol)
            if financial_data is not None and not financial_data.empty:
                st.table(financial_data)
            else:
                st.write("매출 및 영업이익 데이터를 가져올 수 없습니다.")
            
        else:
            st.write("기업 정보를 가져올 수 없습니다. 올바른 기업명인지 확인해주세요.")
    else:
        st.write("입력한 기업명에 해당하는 티커 심볼을 찾을 수 없습니다.")
else:
    st.write("기업명을 입력해 주세요.")

# 저장된 모든 기업 정보 표시
st.write("## 저장된 기업 정보")
with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM companies", conn)
    st.dataframe(df)

