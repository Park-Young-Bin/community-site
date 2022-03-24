# !pip install --upgrade pip (cmd에서 실행) # 구현하기 전 필요한 설치 과정(1)
!pip install streamlit_folium # 구현하기 전 필요한 설치 과정(2)
!pip install geopandas
# 구글드라이브에 있는 png, xlsx, html 파일을 모두 다운받아 작업할 경로에 모두 저장한다!
import pandas as pd
import geopandas as gpd
import folium
import folium.plugins as plug
from streamlit_folium import folium_static
import json
import numpy as np
import math
import streamlit as st
import datetime as dt
import streamlit.components.v1 as components

#나중에 배포 전에 손 볼 것들 
st.set_page_config(page_title="장애인을 위한 체육시설 커뮤니티",          
    page_icon="😋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/LAB-703',
        'Report a bug': "https://github.com/LAB-703",
        'About': '''SPDX-FileCopyrightText: © 2021 Lee Jeong Min
        SPDX-License-Identifier: BSD-3-Clause'''
    }
)

@st.cache(allow_output_mutation=True, persist=True)
def get_data():
    return []

#전체 폰트 설정 
st.markdown("""
        <style>
@font-face {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  src: url(https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css) format('woff');
}
    html, body, [class*="css"]  {
    font-family: 'Pretendard';
    font-size: 20px;
    }
    </style>""",unsafe_allow_html=True)

#전체 배경
page_bg_img = '''
<style> 
.stApp {
  background-image: url("https://capsule-render.vercel.app/api?type=waving&&color=0:FFEEDA,100:F89517&height=70");
  background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown('<p align="center" style=" font-size: 50px;"><b>장애인을 위한 체육시설 커뮤니티</b></p>', unsafe_allow_html=True)

select_event = st.sidebar.selectbox("선택하세요.", ("0️⃣ 서울시 공공체육시설 지도", "1️⃣ 농구장", "2️⃣ 배구장","3️⃣ 배드민턴장", "4️⃣ 수영장", "5️⃣ 실내체육관","6️⃣ 야구장","7️⃣ 족구장","8️⃣ 체력단련실","9️⃣ 축구장","1️⃣0️⃣ 테니스장","1️⃣1️⃣ 풋살장","1️⃣2️⃣ 기타"))

###########################데이터 처리 공간#################################################################
sports=pd.read_excel("공유누리체육시설(서울).xlsx") # 본인 pc에 저장된 파일 경로 입력 필수!
sports=sports.drop(sports.columns[0],axis=1)

#### 숫자열 형변환 후 문자열과 결합

sports['카카오맵']="https://map.kakao.com/link/to/"+sports['자원명칭']+","+sports['위도'].astype(str)+","+sports['경도'].astype(str)

sports=sports.replace(np.nan,"문의") #NaN 대체

#.reset_index(drop=True) => 인덱스 번호가 추출한 그대로 남아있어서 리셋시킴
#.drop(농구장.columns[0],axis=1) 기존 인덱스 떨굼
농구장=sports[sports.자원분류=="농구장"].reset_index(drop=True)
배구장=sports[sports.자원분류=="배구장"].reset_index(drop=True)
배드민턴장=sports[sports.자원분류=="배드민턴장"].reset_index(drop=True)
수영장=sports[sports.자원분류=="수영장"].reset_index(drop=True)
실내체육관=sports[sports.자원분류=="실내체육관"].reset_index(drop=True)
야구장=sports[sports.자원분류=="야구장"].reset_index(drop=True)
족구장=sports[sports.자원분류=="족구장"].reset_index(drop=True)
체력단련실=sports[sports.자원분류=="체력단련실"].reset_index(drop=True)
축구장=sports[sports.자원분류=="축구장"].reset_index(drop=True)
테니스장=sports[sports.자원분류=="테니스장"].reset_index(drop=True)
풋살장=sports[sports.자원분류=="풋살장"].reset_index(drop=True)
기타=sports[sports.자원분류=="기타"].reset_index(drop=True)



# 시군구 지리정보 불러오기
seoul_gu = "서울특별시 시군구 위치 데이터(5179).geojson"
seoul_gu = gpd.read_file(seoul_gu, encoding='euc-kr') # 본인 pc에 저장된 파일 경로 입력 필수!
seoul_gu=seoul_gu.drop(['BASE_DATE'],axis=1)


#################################함수##################################################################
@st.cache(suppress_st_warning=True)
#평균 평점 계산 함수
def rating(x):
    int=math.floor(x)
    dcm=round(x-int,1)
    
    rep=np.repeat('🌕',int)
    
    if dcm==0.5 :
        half='🌗'
    elif dcm>0 and dcm<0.5:
        half='🌘'
    elif dcm>0.5 and dcm<1:
        half='🌖'
    else :
        half='  '

    return "".join(rep)+half
#slider 적용함수 
def slider(index,emoji) :
    name=st.slider(index,1,5,5)
    y=np.repeat(emoji,name)
    st.write("".join(y))
    st.write("")
    return name
    
# 자원별 지도 생성 함수
def mapping(df_name,i,image):
    center = [df_name['위도'][i]+0.005,df_name['경도'][i]]  #마커를 아래로 내려서 팝업이 가리지 않게 
    map = folium.Map(location=center, zoom_start=15)
    folium.GeoJson(seoul_gu, name='Seoul').add_to(map)
    marker_cluster = plug.MarkerCluster().add_to(map)
    iframe ='''<style>th,td {padding:5px;}</style>
    <p style="font-size:15px;text-align:center;"><b>'''+str(df_name[df_name.columns[1]][i])+"</b></p>"+'''
    <table border=0 align="center"> 
        <tr> 
            <td style=""><b>'''+df_name.columns[0]+'''</b> </td>folium_static
            <td  style="text-align:right;">'''+df_name[df_name.columns[0]][i]+'''</td>
        </tr>
        <tr>
            <td><b>'''+df_name.columns[8]+'''</b></td>
            <td  style="text-align:right;">'''+df_name[df_name.columns[8]][i]+'''</td>
        </tr>
        <tr>
            <td><b>'''+df_name.columns[9]+'''</b></td>
            <td  style="text-align:right;">'''+df_name[df_name.columns[9]][i]+'''</td>
        </tr>
        <tr>
            <td><b>'''+df_name.columns[12]+'''</b></td>
            <td  style="text-align:right;">'''+df_name[df_name.columns[12]][i]+'''</td>
        </tr>
    </table>
    <table border=0 align="center">
        <tr>
            <td> <A href="'''+df_name[df_name.columns[21]][i]+'''"> <IMG src="https://github.com/LAB-703/dweer/blob/main/%EC%B9%B4%EC%B9%B4%EC%98%A4.png?raw=true" height="30" border="3"> </A>
            </td>
            <td> <A href="'''+df_name[df_name.columns[21]][i]+'''"> <IMG src="https://github.com/LAB-703/dweer/blob/main/rate.png?raw=true" height="30" border="3"> </A>
            </td>
    </table>'''
    popup = folium.Popup(iframe, min_width=200, max_width=300,show=True)
    icon = folium.features.CustomIcon(image+".png",icon_size=(35, 35))
    folium.Marker([df_name['위도'][i],df_name['경도'][i]], popup=popup, icon=icon).add_to(marker_cluster)
    return folium_static(map)  
#################################0️⃣ 서울시 공공체육시설 지도############################################
if select_event == '0️⃣ 서울시 공공체육시설 지도':
    HtmlFile = open("공공체육시설(서울) 클러스터링 시각화(최종).html", 'r',encoding='utf-8') # 본인 pc에 저장된 파일 경로 입력 필수!
    source_code = HtmlFile.read() 
    print(source_code)
    components.html(source_code, width=1200, height=800,  scrolling=False)

###########################################4️⃣ 수영장##################################################
use_list=[2,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
if select_event == '4️⃣ 수영장':
    m,blank2,columns,attribute=st.columns([10,1,3,6])    
    with m :
        mapping(수영장,1,"swimming")
        st.write("") 
    with blank2 :    
        st.write("")
    with columns :
        for i in use_list:
            if 수영장.iloc[1][i]!=np.NAN: 
                st.markdown(수영장.columns[i])
    with attribute :
        for i in use_list:  
            if 수영장.iloc[1][i]!=np.NAN: 
                st.markdown(수영장.iloc[1][i])

    "-----------------------"  
    rate,blank, review=st.columns([9,2,8])    
    with rate :
        "# 시설에 대해 평가해 주세요."
        access=st.slider("접근성",1,5,5)
        y=np.repeat("👩‍🦽",access)
        st.write("".join(y))
        st.write("")
        safe=st.slider("안전성",1,5,5)
        y=np.repeat("👩‍",safe)
        st.write("".join(y))
        st.write("")
        amenity=st.slider("쾌적성",1,5,5)
        y=np.repeat("✨",amenity)
        st.write("".join(y))
        st.write("")
        "# 시설에 대한 좋은 점, 아쉬운 점을 남겨 주세요."
        menu_list=st.text_area("*작성한 후기는 공개되며, 부적절한 후기는 삭제될 수 있습니다.",max_chars=140,placeholder="서로를 배려하는 마음을 담아 작성해 주세요.")
        date = st.date_input("방문한 날짜",dt.date.today(),max_value = dt.date.today())
        weekday = dt.date.weekday(date)
        dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}
        st.write(date, dateDict[weekday])
        submit=st.button('등록')

        if submit==True:
            st.write('등록이 완료되었습니다.')

            get_data().append({
                "작성일" : dt.datetime.now(),
                "접근성": access, "안전성": safe, "쾌적성": amenity,
                "후기" : menu_list,
                "방문일" : date
            })
    with blank :    
        st.write("")
    with review:   
        df=pd.DataFrame(get_data())
        try :
            mean_안전성=df['안전성'].mean()
            mean_쾌적성=df['쾌적성'].mean()
            st.write("# 전체 평점 (",str(len(df)),"건)")
            st.write("접근성 |",rating(df['접근성'].mean()),round(df['접근성'].mean(),1))
            st.write("안전성 |",rating(df['안전성'].mean()),round(df['안전성'].mean(),1))
            st.write("쾌적성 |",rating(df['쾌적성'].mean()),round(df['쾌적성'].mean(),1))
        except :
            "아직 평점이 없습니다."
        st.write("# 최신 후기")
        st.write("---")
        try :
            st.write("접근성 👩‍🦽",df.iloc[-1][1],"| 안전성 👩‍",df.iloc[-1][2],"| 쾌적성 ✨",df.iloc[-1][3],"방문일 : ",df.iloc[-1][5])
            st.write(df.iloc[-1][4])
            "---"
            st.write("접근성 👩‍🦽",df.iloc[-2][1],"| 안전성 👩‍",df.iloc[-2][2],"| 쾌적성 ✨",df.iloc[-2][3],"방문일 : ",df.iloc[-2][5])
            st.write(df.iloc[-2][4])
            "---"
            st.write("접근성 👩‍🦽",df.iloc[-3][1],"| 안전성 👩‍",df.iloc[-3][2],"| 쾌적성 ✨",df.iloc[-3][3],"방문일 : ",df.iloc[-3][5])
            st.write(df.iloc[-3][4])
        except:
            "아직 후기가 없습니다."












