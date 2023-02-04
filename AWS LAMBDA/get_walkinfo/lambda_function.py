# kind_info dog_breeds 로 join
# category_info : 권장 횟수(walks_number), 권장 시간(min_time, max_time), 권장 거리(min_distance, max_distance)
# walk_info : 오늘 산책 횟수, 권장시간이랑 거리에서 얼마나 채웠는지
import sys
import logging
import pymysql
import os
import json
import datetime
  
def lambda_handler(event, context):
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()
    
    #쿼리문 작성
    regist_num = event.get('regist_num')
    
    # sql = "select * from dog_info, kind_info where dog_info.regist_num='{}'".format(regist_num) + "and dog_info.kind_info_dog_kind = kind_info.dog_kind"
    sql = "select kind_info_dog_kind from dog_info where dog_info.regist_num='{}'".format(regist_num)
    
    #작성한 쿼리문 실행
    curs.execute(sql)
    
    #쿼리문 실행 결과 rows에 저장
    rows = curs.fetchall()[0][0] #dog_kind
    
    #특정 강아지 산책 정보
    sql1 = "select walk_start_time,walk_end_time,total_walk_time, distance,total_num_steps from walk_info where regist_num='{}'".format(regist_num)
    #sql1 = "select * from walk_info where regist_num='{}'".format(regist_num)
    
    curs.execute(sql1)    
    rows1 = curs.fetchall()
    #new = json.dumps(rows1, default=str)
    
    result = []
    #rows 값 result 배열에 삽입
    for i in range(len(rows1)):
        result.append([])
        for j in rows1[i]:
            if type(j)==datetime.datetime:
                result[i].append(j.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                result[i].append(j)
    
    print(result)
    #확인된 견종으로부터 카테고리 확인 절차
    sql2 = "select dog_breeds from kind_info where dog_kind='{}'".format(rows)
    
    curs.execute(sql2)    
    rows2 = curs.fetchall()[0][0] #dog_category
    
    #확인된 카테고리로부터 정보 확인
    sql3 = "select walks_number,min_time,max_time,min_distance,max_distance from category_info where dog_breeds='{}'".format(rows2)
    
    curs.execute(sql3)    
    rows3 = curs.fetchall()    
    
    conn.close()
    
    return {
        "category_walk" : rows3,
        "dog_walk" : result
    }
    # return {
    #     'statusCode': 200,
    #     'items':result,
    #     'event': event,
    # }