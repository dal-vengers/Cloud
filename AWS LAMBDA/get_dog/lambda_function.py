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
    user_id = event.get('user_id')
    
    if regist_num == None:
        sql = "select * from dog_info where user_id='{}'".format(user_id)
    else:
        sql = "select * from dog_info where regist_num={}".format(regist_num)
    
    #작성한 쿼리문 실행
    curs.execute(sql)
    
    #쿼리문 실행 결과 rows에 저장
    rows = curs.fetchall()

    result = []
    #rows 값 result 배열에 삽입
    for i in range(len(rows)):
        result.append([])
        for j in rows[i]:
            if type(j)==datetime.date:
                result[i].append(j.strftime("%Y"+"-%m"+"-%d"))
            else:
                result[i].append(j)

    conn.close()
    return {
        'statusCode': 200,
        'items':result,
        'event': event,
    }