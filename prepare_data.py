import streamlit as st
import pandas as pd
import numpy as np

EXECUTIVES_DATA_URL='./data/big_df_members.csv'
SHAREHOLDER_DATA_URL='./data/big_df_share.csv'
STOCKS_DATA_URL='./data/big_df_stocks.csv'

@st.cache_data
def load_executives_data() -> pd.DataFrame:
    df = pd.read_csv(EXECUTIVES_DATA_URL, dtype=str)
    return df

@st.cache_data
def get_companylist(df: pd.DataFrame) -> np.ndarray:
    all_company = df['종목명'].unique()
    return all_company

@st.cache_data
def load_shareholder_data():
    df_shareholder = pd.read_csv(SHAREHOLDER_DATA_URL, dtype={'corp_code': str,
                                                              '종목명': str, 
                                                              '연도': int,
                                                              '분기': int,
                                                              '성명': str,
                                                              '관계': str,
                                                              '주식 종류': str,
                                                              '기초 소유 주식 수': str,
                                                              '기초 소유 주식 지분 율': float,
                                                              '기말 소유 주식 수': str,
                                                              '기말 소유 주식 지분 율': float})
    
    df_shareholder.rename(columns={"기초 소유 주식 지분 율": "기초 지분율",
                                    "기초 소유 주식 수": "기초 주식수",
                                    "기말 소유 주식 지분 율": "지분율",
                                    "기말 소유 주식 수": "주식수"}, inplace=True)

    df_shareholder['기간'] = df_shareholder['연도'].astype('str') + " - " + df_shareholder['분기'].astype('str')

    df_stocks = pd.read_csv(STOCKS_DATA_URL, dtype={'종목코드': str,
                                                    '종목명': str, 
                                                    'corp_code': str,
                                                    '연도': int,
                                                    '분기': int,
                                                    '회사명': str,
                                                    '법인명': str,
                                                    '출자 목적': str,
                                                    '기초 잔액 수량': str,
                                                    '기초 잔액 지분 율': str,
                                                    '기초 잔액 장부 가액': str,
                                                    '증가 감소 취득 처분 수량': str,
                                                    '증가 감소 취득 처분 금액': str,
                                                    '증가 감소 평가 손액': str,
                                                    '기말 잔액 수량': str,
                                                    '기말 잔액 지분 율': str,
                                                    '기말 잔액 장부 가액': str,
                                                    '최근 사업 연도 재무 현황 총 자산': str,
                                                    '최근 사업 연도 재무 현황 당기 순이익': str})

    df_stocks['기간'] = df_stocks['연도'].astype('str') + " - " + df_stocks['분기'].astype('str')

    corps = df_shareholder['종목명'].unique()
    corp_codes = df_shareholder['corp_code'].unique()
    corp_dict = dict(zip(corp_codes, corps))

    df_shareholder.sort_values(by=['연도', '분기', '지분율'], ascending=False, inplace=True)

    return df_shareholder, df_stocks, corps, corp_codes, corp_dict