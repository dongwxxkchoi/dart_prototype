# Libraries
import streamlit as st

from streamlit_agraph import agraph, Config
from prepare_data import load_shareholder_data
from utils.utils_shareholders import is_target_stock, filter_share_data, filter_stocks_data, make_company_nodes, chase_change, shareholder_change_to_df, add_node_edge

st.set_page_config(page_title='지분관계', page_icon=':bar_chart:', layout='wide')

#######################load&process data########################
df, df_stocks, corps, corp_codes, corp_dict = load_shareholder_data()

###################make company nodes#####################
nodes_dict = make_company_nodes(corp_dict)

######################make side bar########################
st.sidebar.header("분류")
st.sidebar.subheader("회사")

selected_corp_name=st.sidebar.selectbox("Select Company", corps)
selected_corp=df[df['종목명']==selected_corp_name]['corp_code'].unique()[0]

c1, c2 = st.sidebar.columns(2)
c1.subheader("from")
from_duration = c1.selectbox(label="select from", options=df['기간'].unique())

c2.subheader("to")
to_duration = c2.selectbox(label="select to", options=df[df['기간'] >= from_duration]['기간'].unique())
duration = df[(df['기간'] >= from_duration) & (df['기간'] <= to_duration)]['기간'].unique()


###########################home#############################

def home():
    # make nodes and edges for network
    
    st.title("선택한 회사의 지분 관계")
    st.markdown("#")
    
    df_selection=df.query(
        "기간 in @duration & 종목명==@selected_corp_name"
    )   
    df_stocks_selection=df_stocks.query(
        "기간 in @duration & 종목명==@selected_corp_name"
    )

    st.subheader("주주 현황")
    show_data=st.multiselect('Filter: ',df_selection.columns, default=["연도", "분기", "주식 종류", "성명", "관계", "지분율", "주식수"])
    placeholder = st.empty()

    with placeholder.container():
        btn = st.button("보통주만 보기")
    
    if btn:
        df_selection = is_target_stock(df_selection)
        placeholder.empty()
        st.button("우선주도 보기")

    st.dataframe(df_selection[show_data],use_container_width=True, hide_index=True)
    
    st.subheader("타법인 출자 현황")
    show_data_stocks=st.multiselect('Filter: ',df_stocks_selection.columns, default=["연도", "분기", "법인명", "출자 목적", "기말 잔액 수량", "기말 잔액 지분 율"])
    st.dataframe(df_stocks_selection[show_data_stocks], use_container_width=True, hide_index=True)

    if from_duration != to_duration:
        share_section_dict = chase_change(df_selection, to_duration)
        if bool(share_section_dict) is True:
            st.subheader("선택한 기간 동안 지분 변화가 있는 주주")
            col1, col2 = st.columns(2)
            selected_shareholder = col1.selectbox(label='shareholders: ', options=share_section_dict.keys())

            st.dataframe(shareholder_change_to_df(share_section_dict[selected_shareholder]), hide_index=True)

    st.subheader("지분 네트워크")
    col1, _ = st.columns(2)

    selected_year, selected_quarter=col1.selectbox(label='Durations: ', options=duration).split(' - ')
    
    placeholder2 = st.empty()
    with placeholder2.container():
        btn2 = st.button("투자 현황 네트워크")
    
    if btn2:
        placeholder2.empty()
        st.button("회사 지분관계 네트워크")
        nodes, edges = add_node_edge(df_stocks, nodes_dict, selected_corp, selected_year, selected_quarter, shareholder=False)
        config = Config(width=1000, height=1000, directed=True, physics=True, hierarchical=True)
        agraph(nodes=nodes, edges=edges, config=config)   
    
    else:
        nodes, edges = add_node_edge(df, nodes_dict, selected_corp, selected_year, selected_quarter, shareholder=True)

        config = Config(width=600, height=600, directed=True, physics=True, hierarchical=True)
        agraph(nodes=nodes, edges=edges, config=config)

home()