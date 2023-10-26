# Libraries
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from numerize.numerize import numerize

from prepare_data import load_executives_data, get_companylist
from utils.utils_executives import convert_to_csv, executives_change_to_df

st.set_page_config(page_title='임원목록', page_icon=':bar_chart:', layout='wide')

DATA_URL='./data/big_df_members.csv'
theme_plotly = None # None or streamlit

############################################################
# load data #

df = load_executives_data()
company_list = get_companylist(df)

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

def Home():
    st.title("선택한 회사의 임원진 목록")
    st.markdown("#")

    # ============================================================
    # 선택한 회사의 임원 목록
    st.subheader("임원 목록")
    
    df_selection=df.query(
        "연도==@year & 분기==@quarter & 종목명==@selected_company"
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

    period_df = executives_change_to_df(df_selection, selected_name)
    st.download_button('Download file', 
                       data=convert_to_csv(period_df), 
                       file_name=f'{selected_name}-기간별주요이력.csv',
                       mime='text/csv')
    
    st.dataframe(period_df)


Home()