# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize

st.set_page_config(page_title='임원목록', page_icon=':bar_chart:', layout='wide')

DATA_URL='./data/big_df_members.csv'

st.title("🔔 임원진 목록 집중 탐구 🔎")
st.markdown("#")

theme_plotly = None # None or streamlit


############################################################
# load data #

@st.cache_data
def load_data(nrows):
    df = pd.read_csv(DATA_URL, nrows=nrows, dtype=str)
    df.columns =['연도', '분기', '회사명', '시장구분', '성명', '출생년월', '성별', '직위', '등기임원여부', '상근여부', '담당업무', '최대주주와의관계', '재직기간', '임기만료일', 'pid', '주식코드']
    # df.rename(df, axis='columns', inplace=True)
    # print(df)
    return df

df = load_data(330000)

@st.cache_data(max_entries=10)   #-- Magic command to cache data
def get_companylist():
    all_company = df['회사명'].unique()
    all_company.sort()
    return all_company

company_list = get_companylist()

############################################################
# side bar #

st.sidebar.header("분류")

st.sidebar.subheader("회사")
selected_company=st.sidebar.selectbox("Select Company", company_list)

st.sidebar.subheader("연도")
year=st.sidebar.multiselect(
    "Select year",
     options=df["연도"].unique(),
     default=df["연도"].unique(),
)

st.sidebar.subheader("분기")
quarter=st.sidebar.multiselect(
    "Select quarter",
     options=sorted(df["분기"].unique()),
     default=sorted(df["분기"].unique()),
)

######################################################
# Home # 

@st.cache_data
def convert_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8-sig')


def Home():
    # ============================================================
    # 선택한 회사의 임원 목록
    st.subheader("선택한 회사의 임원 목록")
    
    df_selection=df.query(
        "연도==@year & 분기==@quarter & 회사명==@selected_company"
    )   
    showData=st.multiselect('Filter: ',df_selection.columns, default=["연도", "분기", "성명", "출생년월", "성별", "직위"])
    st.download_button(label='Download file', 
                       data=convert_to_csv(df_selection[showData]), 
                       file_name=f'{selected_company}-임원목록.csv',
                       mime='text/csv')
    st.dataframe(df_selection[showData],use_container_width=True)
    
    # ============================================================
    # 선택한 임원의 경력
    st.subheader("선택한 임원의 경력")

    name_list = df_selection[showData]['성명'].unique()
    birth_list = [df_selection[df_selection[showData]['성명'] == name]['출생년월'].unique() for name in name_list]
    
    target_list = []
    for name, birth in zip(name_list, birth_list):
        target_list.append(name + " (" + birth[0] + ")")


    selected_name=st.selectbox(label='Names: ', options=target_list).split("(")[0].strip()
    target_cols = ['연도', '분기', '시장구분', '성별', '직위', '등기임원여부', '상근여부', '담당업무', '최대주주와의관계', '재직기간', '임기만료일']
    st.download_button(label='Download file', 
                       data=convert_to_csv(df_selection[target_cols][df_selection['성명'] == selected_name]), 
                       file_name=f'{selected_name}-이력.csv',
                       mime='text/csv')
    st.dataframe(df_selection[target_cols][df_selection['성명'] == selected_name], use_container_width=True)
    
    # ============================================================
    # 선택한 임원의 기간별 경력
    st.subheader("선택한 임원의 기간별 경력")

    group_df = df_selection[df_selection['성명'] == selected_name][['연도', '분기', '직위','등기임원여부','담당업무','최대주주와의관계']]
    group_df['기간'] = group_df['연도'] + '-' + group_df['분기']
    group_df.drop(['연도', '분기'], axis=1, inplace=True)
    group_df = group_df.groupby(by=['직위', '등기임원여부', '담당업무', '최대주주와의관계'])
    datas = {
        '기간': [],
        '직위': [],
        '등기임원여부': [],
        '담당업무': [],
        '최대주주와의관계': [],
    }

    for key in group_df.groups.keys():
        duration = list(group_df.get_group(key)['기간'].values)
        started = min(duration)
        ended = max(duration)
        
        datas['직위'].append(key[0])
        datas['등기임원여부'].append(key[1])
        datas['담당업무'].append(key[2])
        datas['최대주주와의관계'].append(key[3])
        datas['기간'].append(started+" - "+ended)
    
    period_df = pd.DataFrame(datas)
    st.download_button('Download file', 
                       data=convert_to_csv(period_df), 
                       file_name=f'{selected_name}-기간별주요이력.csv',
                       mime='text/csv')
    
    period_df.sort_values(by="기간", inplace=True)
    st.dataframe(period_df)


Home()