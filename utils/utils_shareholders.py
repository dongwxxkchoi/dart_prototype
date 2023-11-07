import streamlit as st
import pandas as pd
from streamlit_agraph import Node, Edge
from collections import defaultdict

target_stock_types = ['보통주', '의결권 있는 주식', '보통주식', '의결권있는주식', '의결권 있는보통주', '의결권 있는 주식(보통주)', '의결권있는 주식', '기명식보통주', '의결권이 있는 주식', '보통주(의결권있는주식)', '보통주(DR)', '보통주(의결권 있는 주식)', '의결권 있는주식', '보통주(의결권있음)', '의결권 있는 보통주식', '의결권유', '의결권있는보통주', '전환우선주', '전환주', '보통주,전환우선주', '의결권 있는 주식', '기초 : 우선주기말 :보통주', '보통주/우선주', '의결권있는주식(보통주)', '전환상환우선주', '우선주보통주', '상환전환우선주', '의결권있는 보통주식', '의결권 있는 우선주', '의결권이있는 주식']

def is_target_stock(df: pd.DataFrame):
    df = df.loc[df['주식 종류'].isin(target_stock_types)]
    return df

# 필요한 칼럼만 남깁니다.
# prototype은 보통주만 남깁니다.
# year과 quarter가 주어졌다면, 해당하는 필터로 거릅니다.
def filter_share_data(df, corp_code, year=None, quarter=None):
    shareholders_df = df[:]
    shareholders_df = is_target_stock(shareholders_df)

    if year is not None:
        shareholders_df = shareholders_df.loc[shareholders_df['연도'] == int(year)]
    if quarter is not None:
        shareholders_df = shareholders_df.loc[shareholders_df['분기'] == int(quarter)]

    shareholders_df = shareholders_df[shareholders_df['corp_code'] == corp_code][['성명', '지분율']]
    
    return shareholders_df

def filter_stocks_data(df, corp_code, year=None, quarter=None):
    stocks_df = df[:]

    if year is not None:
        stocks_df = stocks_df.loc[stocks_df['연도'] == int(year)]

    if quarter is not None:
        stocks_df = stocks_df.loc[stocks_df['분기'] == int(quarter)]


    stocks_df = stocks_df[stocks_df['corp_code'] == corp_code][['법인명', '기말 잔액 지분 율']]
    
    return stocks_df

def get_corp_data(df, corp_code):
    corp_list = []
    shareholders_df = df[df['corp_code'] == corp_code][['주주', 'shareholder_code', '지분율']]
    corp_list += shareholders_df[shareholders_df['shareholder_code'] != "-"]['주주'].values.tolist()
    stocks_df = df[df['shareholder_code'] == corp_code][['corp_code', '종목명', '지분율']]
    corp_list += stocks_df[stocks_df['corp_code'] != "-"]['종목명'].values.tolist()

    return corp_list

@st.cache_data
def make_company_nodes(corp_dict):
    nodes_dict = {}
    for corp_code, stock in corp_dict.items():
        nodes_dict[corp_code] = Node(id=corp_code, label=stock, size=25, shape="square")
        # shape -> image, circularImage, diamond, dot, star, triangle, triangleDown, hexagon, square and icon

    return nodes_dict

#######################chase change#########################
def return_next_duration(duration):
    year, quarter = map(int, duration.split(' - '))
    if quarter == 4:
        next_year = year + 1
        next_quarter = 1
    else:
        next_year = year
        next_quarter = quarter + 1
    return f"{next_year} - {next_quarter}"



def chase_change(df, to_duration, shareholder=True):
    if shareholder:
        df.sort_values(by=["기간", "주식수", "지분율"], ascending=[True, False, False])
        df = is_target_stock(df)
        names = df['성명'].unique()
        object_dict = defaultdict(list)
        section_dict = {}

        for i, row in df.iterrows():    
            object_dict[row['성명']].append([row['기간'], row['주식수'], row['지분율']])
        
        for name in names:
            if object_dict[name][0][0] != to_duration:
                object_dict[name].insert(0, [return_next_duration(object_dict[name][0][0]), '0', 0])
            stock_share = [tuple(row[1:]) for row in object_dict[name]]
            duration_stock_share = object_dict[name]

            if not all(x == stock_share[0] for x in stock_share):
                object_data = sorted(duration_stock_share)
                unique_data = sorted(list(set(stock_share)))
                
                index = -1
                section = []
                for i, row in enumerate(object_data):
                    this_index = unique_data.index(tuple(row[1:]))
                    if index != this_index:
                        index = this_index
                        section.append(row)
                    if i == len(object_data)-1:
                        section.append(row)
                
                section_dict[name] = section

        return section_dict


def shareholder_change_to_df(shareholder_change_info):
    processed = []
    
    for i, data in enumerate(shareholder_change_info):
        if data[0] != shareholder_change_info[i+1][0]:
            processed.append([data[0]+" ~ "+shareholder_change_info[i+1][0], data[1], data[2]])
        else:
            processed.append([data[0], data[1], data[2]])
        if i == len(shareholder_change_info) - 2:
            break

    processed_df = pd.DataFrame(processed, columns=['기간','주식수','지분율'])
    processed_df.sort_values(inplace=True, ascending=False, by="기간")
    return processed_df

def add_node_edge(df, nodes_dict, corp_code, year, quarter, shareholder=True):
    nodes, edges = [], []
    
    # 해당 기업의 노드를 중심에 추가
    nodes.append(nodes_dict[corp_code])

    if shareholder:
        # year, quarter로 1차 필터링
        df = filter_share_data(df, corp_code, year, quarter)
    else:
        df = filter_stocks_data(df, corp_code, year, quarter)

    for _, row in df.iterrows():
        if shareholder:
            size = row['지분율']
            temp_id = row['성명']+" - "+str(row['지분율'])
            if size > 0:
                if size < 1:
                    nodes.append(Node(id=temp_id, label=row['성명'], size=10, color="#008000"))
                else:
                    nodes.append(Node(id=temp_id, label=row['성명'], size=10+size, color="#008000"))
                    
                edges.append(Edge(source=temp_id, target=corp_code, color="#FF6347"))
        else: 
            size = row['기말 잔액 지분 율']
            temp_id = row['법인명']+" - "+str(row['기말 잔액 지분 율'])
            nodes.append(Node(id=temp_id, label=row['법인명'], size=10, color="#008000"))
        
            edges.append(Edge(source=corp_code, target=temp_id, color="#2E2EFE"))
    
    return nodes, edges