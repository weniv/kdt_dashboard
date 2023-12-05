import streamlit as st
import pandas as pd
import requests
import json
import datetime
from urllib.parse import quote


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

tab_weniv, tab_rank = st.tabs(['위니브 KDT 목록', 'KDT 목록'])

# --------------------[데이터 관련]--------------------
# 목록 API 불러오기    
def list_api(start_date, end_date, tr_option, tr_name, tr_company):
    df = pd.DataFrame({})

    for i in range(1,11):
        df_new,x = list_api_param(i,start_date,end_date,tr_option,tr_name,tr_company)
        df = pd.concat([df,df_new])
    
    return df
    
# def list_api_100plus():
#     df,data_count=list_api_param(list_url,1)
#     for i in range(2,int(data_count/100)+1):
#         df_new,x = list_api_param(list_url,i)
#         df = pd.concat([df,df_new])

def list_api_param(i,start_date,end_date,tr_option,tr_name,tr_company):
    list_url = 'https://www.hrd.go.kr/jsp/HRDP/HRDPO00/HRDPOA60/HRDPOA60_1.jsp'

    params ={
        'authKey' : 'wxIQpuDgcncKjd3VE23AgBwRHGfm5sqd',
        'returnType':'JSON',
        'outType':1, # 1: 리스트, 2:상세 출력
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

    result = content.get('returnJSON')
    result = json.loads(result)
    data_count = result['scn_cnt']
    result = result['srchList']

    df = pd.DataFrame(result)
    columns = ['traStartDate','traEndDate','subTitle','title','regCourseMan','yardMan','courseMan',
               'realMan', 'eiEmplCnt3']

    df = df.reset_index()
    df = df[columns]
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
        'eimplRate3': '고용보험 3개월 취업률',
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
    list_url = 'https://www.hrd.go.kr/jsp/HRDP/HRDPO00/HRDPOA60/HRDPOA60_1.jsp'
    
    params ={
        'authKey' : 'wxIQpuDgcncKjd3VE23AgBwRHGfm5sqd',
        'returnType':'JSON',
        'outType':1, #  - 1: 리스트, 2:상세 출력
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

    result = content.get('returnJSON')
    result = json.loads(result)
    result = result['srchList']

    df = pd.DataFrame(result)
    return df

list_kdt_name = ['[스마트훈련]데이터 사이언티스트 실무과정','ESTsoft 백엔드 개발자 양성 과정']

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

# --------------------[데이터 시각화]--------------------
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

with tab_rank:
    with st.expander("옵션 선택"):
        s_col1_1, s_col1_2 = st.columns((4, 6), gap = 'large')
        s_col1_1.write('개강 시작/종료일 : ')
        with s_col1_2:
            tr_open = st.date_input("",[datetime.date.today(), datetime.date.today()+datetime.timedelta(days=30)],label_visibility='collapsed')

        s_col2_1, s_col2_2 = st.columns((4, 6), gap = 'large')
        s_col2_1.write('훈련 유형 : ')
        with s_col2_2:
            tr_option = st.multiselect(label = "**훈련유형을 선택해주세요**",
                                        options = ['국민내일배움카드(일반)','국민내일배움카드(구직자)', '국민내일배움카드(재직자)',
                                                    '국가기간전략산업직종','과정평가형훈련','기업맞춤형훈련','스마트혼합훈련','일반고특화훈련',
                                                    '4차산업혁명인력양성훈련','K-디지털 트레이닝','K-디지털 기초역량훈련',
                                                    '플랫폼종사자훈련','산업구조변화대응','중장년경력설계카운슬링','실업자 원격훈련',
                                                    '근로자 원격훈련','근로자 외국어훈련'],
                                        label_visibility = 'collapsed')
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
            tr_name = st.text_input('',placeholder='훈련 과정명을 입력해주세요.',label_visibility='collapsed')
            tr_name = quote(tr_name, safe='')

        s_col4_1, s_col4_2 = st.columns((4, 6), gap = 'large')
        s_col4_1.write('훈련 기관명 : ')
        with s_col4_2:
            tr_company = st.text_input('',placeholder='훈련 기관명을 입력해주세요.',label_visibility='collapsed')
            tr_company = quote(tr_company, safe='')


    df = list_api(tr_open[0],tr_open[1],tr_option_codes,tr_name,tr_company)
    st.dataframe(df)
