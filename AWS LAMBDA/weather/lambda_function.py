import pandas as pd
from bs4 import BeautifulSoup
import requests, json
import pymysql
import os

def crawling(lat, lon):
    url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x=" + lon + "&y=" + lat + "&input_coord=WGS84"
    headers = {"Authorization": "KakaoAK " + os.environ['kakoAK']}
    api_test = requests.get(url, headers=headers)
    url_text = json.loads(api_test.text)
    location = url_text['documents'][0]['region_2depth_name']

    ## 미세먼지 정보
    url = "https://api.odcloud.kr/api/RltmArpltnInforInqireSvrc/v1/getMsrstnAcctoRltmMesureDnsty?numOfRows=1&stationName=" + location + "&dataTerm=DAILY&ver=1.3&serviceKey="
    key = os.environ['key']
    url_1 = url + key  # 지역 설정은 아직 안함.

    html = requests.get(url_1).content

    soup = BeautifulSoup(html, "html.parser")

    '''
    datatime : 측정일
    pm10Grade1h : 1시간 미세먼지 등급 자료
    pm25Grade1h : 1시간 초미세먼지 등급
    미세먼지 그레이드는 1~4가 추출되며
    1 = 좋음, 2 = 보통, 3 = 나쁨, 4 = 매우나쁨으로 나온다.

    '''
    datatime = soup.find('datatime').text
    pm10 = soup.find('pm10grade1h').text
    pm25 = soup.find('pm25grade1h').text
    if pm10 == "1":
        pm10 = "좋음"
    elif pm10 == "2":
        pm10 = "보통"
    elif pm10 == "3":
        pm10 = "나쁨"
    else:
        pm10 = "매우나쁨"

    if pm25 == "1":
        pm25 = "좋음"
    elif pm25 == "2":
        pm25 = "보통"
    elif pm25 == "3":
        pm25 = "나쁨"
    else:
        pm25 = "매우나쁨"

    ### 온습도 정보

    apiKey = os.environ['apikey']
    api = f"https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + apiKey

    result = requests.get(api).content
    soup = BeautifulSoup(result, "html.parser")

    json_object = json.loads(str(soup))
    weather_id = json_object['weather'][0]['id']
    temp = json_object['main']['temp']
    temp = round(temp - 273.15,1)
    humidity = json_object['main']['humidity']
    
    Thunderstorm = [200,201,202,210,211,212,221,230,231,232] # 뇌우
    Drizzle = [300,301,302,310,311,312,313,314,321]#이슬비.
    Rain = [500,501,502,503,504,511,520,521,522,531] #비
    Snow = [600,601,602,611,612,613,615,616,620,621,622] # 눈
    Fog = [701,721,741] # 안개
    Squall = [771] # 돌풍
    Tornado = [781] # 태풍
    Ash = [762] # 화산재
    Dust = [711,731,751,761] #먼지
    Clear = [800] # 맑음
    Clouds = [801,802,803,804] #구름

    # 날씨 정보가 영어로 전달되고 다양한 문자 구성으로 이루어져, 간단하게 통합하여, 이미지 송출
    if weather_id in Thunderstorm:
        weather_id = "뇌우"
    elif weather_id in Drizzle:
        weather_id = "이슬비"
    elif weather_id in Rain:
        weather_id = "비"
    elif weather_id in Snow:
        weather_id = "눈"
    elif weather_id in Fog:
        weather_id = "안개"
    elif weather_id in Squall:
        weather_id = "돌풍"
    elif weather_id in Tornado:
        weather_id = "태풍"   
    elif weather_id in Ash:
        weather_id = "화산재"
    elif weather_id in Dust:
        weather_id = "먼지"
    elif weather_id in Clear:
        weather_id = "맑음"
    elif weather_id in Clouds:
        weather_id = "구름"
    else:
        pass

    
    location = location + "_" + datatime[-5:-3]
    
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()

    sql = "INSERT INTO sky_info (date_time, weather, temp, humidity, pm10, pm25, location) VALUES ('{}','{}','{}',{},'{}','{}','{}')".format(datatime, weather_id, temp, humidity, pm10, pm25, location)

    curs.execute(sql)
    
    sql_s = "SELECT date_time FROM sky_info WHERE date_time <= DATE_SUB('{}', INTERVAL 2 HOUR)".format(datatime)
    
    curs.execute(sql_s)
    
    rows = curs.fetchall()
    
    if len(rows) < 4:
        conn.commit()
        
    else:
        sql_d = "DELETE FROM sky_info WHERE date_time <= DATE_SUB('{}', INTERVAL 2 HOUR)".format(datatime)
      
        curs.execute(sql_d)
      
        conn.commit()

def lambda_handler(event, context):
    lat1 = "37.51252777344"
    lon1 = "126.939942092863"
    lat2 = "37.5179681611717"
    lon2 = "127.047059839521"
  
    while(True):
        crawling(lat1,lon1)
        crawling(lat2,lon2)