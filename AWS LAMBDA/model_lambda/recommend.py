import pandas as pd
import math
import haversine
import pymysql
import os

def recom(place, like, distance, lat, lng):
    
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()
    
    # 애견카페
    if place == "애견카페":
        if like == "1": 
            category = ['dessert, coffee, drink']
        elif like == "2": 
            category = ['interior, picture, toilet']
        elif like == "3": 
            category = ['animal, space, clean']
        elif like =="4": 
            category = ['goodprice, reasonable, kind']
        else:
            category = ['dessert, coffee, drink, interior, picture, toilet, animal, space, clean, goodprice, reasonable, kind']
    
        sql = "select name, {} from dog_recommend".format(*category)
        curs.execute(sql)
        rpm = curs.fetchall()
    
    # 애견동반카페    
    elif place == "애견동반카페": 
        if like == "1":
            category = ['coffee, drink, dessert, special']
        elif like == "2":
            category = ['interior, view, picture']
        elif like == "3":
            category = ['clean, toilet, seat, focus']
        elif like == "4":
            category = ['goodprice, talk, kind']
        else:
            category = ['coffee, drink, dessert, special, interior, view, picture, clean, toilet, seat, focus, goodprice, talk, kind']
            
        sql = "select name, {} from cafe_recommend".format(*category)
        curs.execute(sql)
        rpm = curs.fetchall()
    
    # 주소 및 좌표 데이터
    sql = "select * from place_info where place_type = '애견동반카페' or place_type = '애견카페'"
    curs.execute(sql)
    addr = curs.fetchall()
    
    lst_map = pd.DataFrame(addr)
    lst_map.set_index(0,inplace=True)
    
    lst = pd.DataFrame(rpm)
    lst.set_index(0,inplace=True) #이름 indexing
    lst = lst.astype(float)
    lst['result'] = lst[lst.columns].sum(axis=1) # 유사도 합
    
    # 점수가 높은 순으로 정렬
    lst.sort_values('result', ascending=False, inplace=True)
    # 점수가 높은 순으로 매장 이름만 뽑아내기.
    result = lst.index

    #가장 가까운 매장 찾기
    # result2는 result에서 잡힌 서열을 순서로 사용자가 원하는 거리 안에 있는 것을 순위에 맞춰 짤라내어 저장하고 있음
    result2 = pd.DataFrame()
    imsi = (lat, lng) # 실시간으로 받아 올 좌표
    x = imsi[0] # 내위치
    y = imsi[1]
    #result는 사용자가 선택한 카테고리에 맞춰 랭킹을 만든 후 랭킹 순위대로 인덱스를 추출한 결과
    for rank in result:
        place_data = (lst_map.loc[rank, 2], lst_map.loc[rank, 3])
        dist = haversine.haversine(imsi, place_data, unit='m')
        if dist < distance:
            result2.loc[rank, "address"] = lst_map.loc[rank, 1]
            result2.loc[rank, "lat"] = lst_map.loc[rank, 2]
            result2.loc[rank, "lng"] = lst_map.loc[rank, 3]
            result2.loc[rank, "dist"] = dist
        if like != "5": # 최단거리를 출력하는 것이 아니라면, 위에서 순위화 하였으니,
            if len(result2) == 5:
                break
    if like == '5': # 최단거리를 출력하는 거라면
        result2.sort_values('dist', inplace=True)
        result2 = result2.iloc[0:5]

    # 근처에 해당 조건의 매장이 없다면
    if len(result2.index) == 0:
        context = {
            "name": "0",
            "lat": 0,
            "lng" : 0,
            "x" : x,
            "y" : y
        }
        return context
        # 근처에 해당 조건의 매장이 있다면,
    else:
    # 자바스크립트에서 읽힐 수 있게 하기위해 딕셔너리로 변환
        name = result2.index
        lat = result2.lat
        lon = result2.lng
        address = result2.address
        result3 = {}
        
        for i in range(len(result2)):
            context = {
                "name":name[i],
                "lat": lat[i],
                "lng" : lon[i],
                "address":address[i]
            }
            result3[i] = context
        return result3