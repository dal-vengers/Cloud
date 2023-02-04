import sys
import logging
import pymysql
import os
import json
import requests

def lambda_handler(event, context):
    lon = 126.9397997
    lat = 37.5124298
    
    url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={}&y={}&input_coord=WGS84".format(lon, lat)
    headers = {"Authorization": "KakaoAK " + "33927ef813f722d8057368bc783fe744"}
    api_test = requests.get(url, headers=headers)
    url_text = json.loads(api_test.text)
    location = url_text['documents'][0]['region_2depth_name']
    
    loc = location[0]
    
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()
    
    sql = "select * from sky_info where location like '{}%'".format(loc)
    
    #작성한 쿼리문 실행
    curs.execute(sql)
    
    #쿼리문 실행 결과 rows에 저장
    rows = curs.fetchall()
    
    result = rows[-1]
    
    conn.close()
    
    return {
        'result':result[1:6]
    }