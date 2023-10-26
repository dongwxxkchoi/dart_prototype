import streamlit as st
import pandas as pd

@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def executives_change_to_df(df, selected_name):
    group_df = df[df['성명'] == selected_name][['연도', '분기', '직위','등기임원여부','담당업무','최대주주와의관계']]
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
    period_df.sort_values(by="기간", inplace=True)

    return period_df