import streamlit as st
import pandas as pd
import requests
import json
import datetime
from urllib.parse import quote

service_key = {
    'ntlc_train' : '9f62fae1-f506-4e5a-be77-ff5385d09f23', # 국민내일배움카드 훈련과정	
    'Common_code' : 'f6060adb-d75b-4fb6-9985-2265a3b7e6b5', # 공통코드	
    'nhrdc_train' : '95017e88-6410-4fd4-b2ac-d45d20b0e709', # 국가인적자원개발 컨소시엄 훈련과정	
}

# --------------------[기본 UI 구성]--------------------
st.set_page_config(
    page_title = 'KDT Dashboard',
    page_icon = '👩‍💻',
    layout = 'wide',
    initial_sidebar_state = 'collapsed',
)

# 대시보드 타이틀
col1, col2, col3 = st.columns((3.5, 5.5, 1))

with col1:
    st.write('')
with col2:
    st.title('KDT Dashboard')  
with col3:
    st.write('')

tab_rank, tab_weniv, tab_est = st.tabs(['KDT 목록','위니브 KDT 목록','이스트 KDT 목록'])

# --------------------[데이터 관련]--------------------
# 목록 API 불러오기    
def list_api(start_date, end_date, tr_option, tr_name, tr_company):
    df = pd.DataFrame({})

    for i in range(1,6):
        df_new,x = list_api_param(i,start_date,end_date,tr_option,tr_name,tr_company)
        df = pd.concat([df,df_new])
    
    return df
    
# def list_api_100plus():
#     df,data_count=list_api_param(list_url,1)
#     for i in range(2,int(data_count/100)+1):
#         df_new,x = list_api_param(list_url,i)
#         df = pd.concat([df,df_new])

def list_api_param(i,start_date,end_date,tr_option,tr_name,tr_company):
    list_url = 'https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do'

    params ={
        'authKey' : '9f62fae1-f506-4e5a-be77-ff5385d09f23',
        'returnType':'JSON',
        'outType':2, # 1: 리스트, 2:상세 출력
        'pageNum':i, 
        'pageSize':100, 
        'srchTraStDt':start_date.strftime("%Y%m%d"),
        'srchTraEndDt':end_date.strftime("%Y%m%d"),
        'sort':'DESC',
        'sortCol':'TOT_FXNUM',
        'crseTracseSe':tr_option,        
        'srchNcs1':'20',
        'srchNcs2':'2001',
        'srchTraProcessNm':tr_name,
        'srchTraOrganNm':tr_company,
    }

    response = requests.get(list_url, params=params)
    content = response.json()

    # result = content.get('returnJSON')
    # result = json.loads(result)
    data_count = content['scn_cnt']
    result = content['srchList']

    df = pd.DataFrame(result)
    new_column_names = {
        'traStartDate':'훈련 시작일',
        'traEndDate': '훈련 종료일',
        'subTitle':'기업명',
        'title':'제목',
        'regCourseMan':'수강신청 인원',
        'yardMan':'정원',
        'courseMan':'수강비',
        'realMan':'실제 훈련비',
        'eiEmplCnt3': '고용보험 3개월 취업인원 수',
        'eiEmplRate3': '고용보험 3개월 취업률',
        'eiEmplRate6': '고용보험 6개월 취업률',
        'trprDegr': '훈련 과정 순차',
        'grade':'등급',
        'trainTarget':'훈련 대상',
        'address': '주소',
        'telNo':'전화번호',
        'titleLink':'제목 링크',
        'subTitleLink':'부제목 링크'
    }

    df = df.rename(columns=new_column_names)
    return df,data_count

# --------------------[위니브 KDT List]--------------------
def weniv_list_api(name):
    list_url = 'https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do'
    
    params ={
        'authKey' : '9f62fae1-f506-4e5a-be77-ff5385d09f23',
        'returnType':'JSON',
        'outType':2, #  - 1: 리스트, 2:상세 출력
        'pageNum':1, 
        'pageSize':100, 
        'srchTraStDt':(datetime.date.today()-datetime.timedelta(days=150)+datetime.timedelta(hours=9)).strftime("%Y%m%d"),
        'srchTraEndDt':(datetime.date.today()+datetime.timedelta(days=365, hours=9)).strftime("%Y%m%d"),
        'sort':'ASC',
        'sortCol':'TRNG_BGDE',
        'srchTraProcessNm': name,
    }

    response = requests.get(list_url, params=params)
    content = response.json()

    # result = content.get('returnJSON')
    # result = json.loads(result)
    result = content['srchList']

    df = pd.DataFrame(result)
    return df

list_kdt_name = ['[스마트훈련]초거대/생성 모델 활용 AI서비스 개발자 실무과정','[이스트캠프] 오르미 프론트엔드 개발(React, HTML/CSS/JavaScript)', '러닝스푼즈 테크런 : 데이터 PM']

weniv_kdt_list=pd.DataFrame({}, columns=[''])

for i in list_kdt_name:
    url_encoded = quote(i, safe='')
    kdt_list = weniv_list_api(url_encoded)
    weniv_kdt_list = pd.concat([weniv_kdt_list,kdt_list])

columns = ['traStartDate','traEndDate','subTitle','title','regCourseMan','yardMan','courseMan','realMan']
weniv_kdt_list = weniv_kdt_list.reset_index()
weniv_kdt_list = weniv_kdt_list[columns]
new_column_names = {
    'traStartDate':'훈련 시작일',
    'traEndDate': '훈련 종료일',
    'subTitle':'기업명',
    'title':'제목',
    'regCourseMan':'수강신청 인원',
    'yardMan':'정원',
    'courseMan':'수강비',
    'realMan':'실제 훈련비',
}
weniv_kdt_list = weniv_kdt_list.rename(columns=new_column_names)

# --------------------[이스트 KDT List]--------------------
# est_kdt_list =list_api(tr_open[0],tr_open[1],tr_option_codes,tr_name,'이스트소프트')

# columns = ['traStartDate','traEndDate','subTitle','title','regCourseMan','yardMan','courseMan','realMan']
# est_kdt_list = est_kdt_list.reset_index()
# est_kdt_list = est_kdt_list[columns]
# new_column_names = {
#     'traStartDate':'훈련 시작일',
#     'traEndDate': '훈련 종료일',
#     'subTitle':'기업명',
#     'title':'제목',
#     'regCourseMan':'수강신청 인원',
#     'yardMan':'정원',
#     'courseMan':'수강비',
#     'realMan':'실제 훈련비',
# }
# est_kdt_list = est_kdt_list.rename(columns=new_column_names)


# --------------------[데이터 시각화]--------------------
def eda(key_suffix, show_company=True):
    with st.expander("옵션 선택"):
        s_col1_1, s_col1_2 = st.columns((4, 6), gap = 'large')
        s_col1_1.write('개강 시작일 : ')
        with s_col1_2:
            tr_open = st.date_input("",[datetime.date.today(), datetime.date.today()+datetime.timedelta(days=30)],label_visibility='collapsed',
                                  key=f"date_{key_suffix}")
        
        s_col2_1, s_col2_2 = st.columns((4, 6), gap = 'large')
        s_col2_1.write('훈련 유형 : ')
        with s_col2_2:
            tr_option = st.multiselect(label = "**훈련유형을 선택해주세요**",
                                        options = ['국민내일배움카드(일반)','국민내일배움카드(구직자)', '국민내일배움카드(재직자)',
                                                    '국가기간전략산업직종','과정평가형훈련','기업맞춤형훈련','스마트혼합훈련','일반고특화훈련',
                                                    '4차산업혁명인력양성훈련','K-디지털 트레이닝','K-디지털 기초역량훈련',
                                                    '플랫폼종사자훈련','산업구조변화대응','중장년경력설계카운슬링','실업자 원격훈련',
                                                    '근로자 원격훈련','근로자 외국어훈련'],
                                        label_visibility = 'collapsed',key=f"multiselect_{key_suffix}")
            tr_option_code = {
                '국민내일배움카드(일반)':'C0061',
                '국민내일배움카드(구직자)': 'C0061S', 
                '국민내일배움카드(재직자)':'C0061I', 
                '국가기간전략산업직종':'C0054', 
                '과정평가형훈련':'C0055C', 
                '기업맞춤형훈련':'C0054G', 
                '스마트혼합훈련':'C0054Y', 
                '일반고특화훈련':'C0054S', 
                '4차산업혁명인력양성훈련':'C0054I', 
                'K-디지털 트레이닝':'C0104', 
                'K-디지털 기초역량훈련':'C0105', 
                '플랫폼종사자훈련':'C0103', 
                '산업구조변화대응':'C0102', 
                '중장년경력설계카운슬링':'C0106', 
                '실업자 원격훈련':'C0055', 
                '근로자 원격훈련':'C0031', 
                '근로자 외국어훈련':'C0031F' 
            }
            
            value = ''

            for key in tr_option:
                if key in tr_option_code:
                    value+=tr_option_code[key]
                    value+=','
                else:
                    value=''

            tr_option_codes = value

        s_col3_1, s_col3_2 = st.columns((4, 6), gap = 'large')
        s_col3_1.write('훈련 과정명 : ')
        with s_col3_2:
            tr_name = st.text_input('',placeholder='훈련 과정명을 입력해주세요.',label_visibility='collapsed',key=f"name_{key_suffix}")
            tr_name = quote(tr_name, safe='')

        tr_company = ''
        if show_company:
            s_col4_1, s_col4_2 = st.columns((4, 6), gap = 'large')
            s_col4_1.write('훈련 기관명 : ')
            with s_col4_2:
                tr_company = st.text_input('',placeholder='훈련 기관명을 입력해주세요.',
                                         label_visibility='collapsed', 
                                         key=f"company_{key_suffix}")
                tr_company = quote(tr_company, safe='')
    
    return {'tr_open':tr_open, 'tr_option_codes':tr_option_codes, 'tr_name':tr_name, 'tr_company':tr_company}


with tab_rank:
    result1 = eda("first", show_company=True)
    try:
        df = list_api(result1['tr_open'][0],result1['tr_open'][1],result1['tr_option_codes'],result1['tr_name'],result1['tr_company'])
    except IndexError:
        tr_open = (datetime.date.today(),datetime.date.today())
        df = list_api(result1['tr_open'][0],result1['tr_open'][1],result1['tr_option_codes'],result1['tr_name'],result1['tr_company'])

    df = df.drop(['eiEmplCnt3Gt10','ncsCd','instCd','trngAreaCd','trprId','trainTargetCd',
                  'trainstCstId','contents','titleIcon'],axis=1)
    columns  = ['훈련 시작일', '훈련 종료일', '기업명', '제목', '수강신청 인원',
       '정원', '수강비', '실제 훈련비', '고용보험 3개월 취업인원 수', '고용보험 3개월 취업률',
       '고용보험 6개월 취업률', '훈련 과정 순차', '등급', '훈련 대상', '주소',
       '전화번호', '제목 링크', '부제목 링크']
    df = df[columns] 
    df = df.reset_index()
    df['수강신청 인원'] = df['수강신청 인원'].astype('int')

    st.dataframe(df)
    
    if df.shape[0]>=500:
        @st.cache_data
        def convert_df(df):
            try:
                # 데이터프레임 내의 모든 문자열 값에서 문제가 되는 특수문자 치환
                # 더 광범위한 특수문자 처리
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str).str.replace('\xa0', ' ')  # 비분리 공백 처리
                    df[col] = df[col].str.replace('\u2013', '-')  # Em dash 처리
                    df[col] = df[col].str.replace('\u2014', '-')  # En dash 처리
                    # 추가 특수문자가 있다면 여기에 더 추가
                
                return df.to_csv(encoding="cp949").encode("cp949")
            except UnicodeEncodeError as e:
                # 어떤 문자가 문제인지 로그로 확인
                print(f"인코딩 오류: {e}")
                
                # 실패 위치의 문자 확인 (에러 메시지에서 위치 추출)
                error_msg = str(e)
                import re
                position_match = re.search(r'position (\d+)', error_msg)
                if position_match:
                    position = int(position_match.group(1))
                    csv_data = df.to_csv()
                    if position < len(csv_data):
                        problem_char = csv_data[position]
                        print(f"문제 문자: {problem_char}, 유니코드: {ord(problem_char):x}")
                
                # 마지막 수단: euc-kr로 시도
                try:
                    return df.to_csv(encoding="euc-kr").encode("euc-kr")
                except:
                    # 모든 방법 실패 시 utf-8 사용
                    return df.to_csv(encoding="utf-8").encode("utf-8")

        csv = convert_df(df)
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name="large_df.csv",
            mime="text/csv",
        )

with tab_weniv:
    # 선택 위젯 레이아웃 설정
    # _, s_col1, _, s_col2 = st.columns((3.8, 1.2, 4, 1), gap = 'large')
    # col1, col2 = st.columns(2, gap = 'large')
    
    # with col1:
    #     col1_1, col1_2, col1_3 = st.columns(3)
    #     col1_1.metric(label="달러USD", value="1,276.20 원", delta="-12.00원")
    #     col1_2.metric(label="일본JPY", value="958.63 원", delta="-7.44 원")
    #     col1_3.metric(label="유럽연합EUR", value="1,335.82 원", delta="11.44 원")
    
    # with col2:
    #     pass

    st.dataframe(weniv_kdt_list, use_container_width=True)

with tab_est:
    result2 = eda("second", show_company=False)
    try:
        df = list_api(result2['tr_open'][0],result2['tr_open'][1],result2['tr_option_codes'],result2['tr_name'],'이스트소프트')
    except IndexError:
        tr_open = (datetime.date.today(),datetime.date.today())
        df = list_api(result2['tr_open'][0],result2['tr_open'][1],result2['tr_option_codes'],result2['tr_name'],'이스트소프트')

    df = df.drop(['eiEmplCnt3Gt10','ncsCd','instCd','trngAreaCd','trprId','trainTargetCd',
                  'trainstCstId','contents','titleIcon'],axis=1)
    columns  = ['훈련 시작일', '훈련 종료일', '기업명', '제목', '수강신청 인원',
       '정원', '수강비', '실제 훈련비', '고용보험 3개월 취업인원 수', '고용보험 3개월 취업률',
       '고용보험 6개월 취업률', '훈련 과정 순차', '등급', '훈련 대상', '주소',
       '전화번호', '제목 링크', '부제목 링크']
    df = df[columns] 
    df = df.reset_index()

    st.dataframe(df)

