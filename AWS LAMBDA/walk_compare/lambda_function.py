import sys
import logging
import pymysql
import datetime, json
import os

def json_default(value):
  if isinstance(value, datetime.date):
    return value.strftime('%Y-%m-%d')
  raise TypeError('not JSON serializable')

def compare_month(today_month, today_day, month, day):
    to_m = [1,3,5,7,8,10,12]
    t_m = [4,6,9,11]

    if int(today_month) >= int(month):
        res_m = int(today_month) - int(month)
        if int(today_day) >= int(day):
            res_d = int(today_day)-int(day)
        else:
            res_d = int(today_day)-int(day)
            if int(month) in to_m:
                res_d += 31
            elif int(month) in t_m:
                res_d += 30
            else:
                res_d += 28

    return res_m, res_d

def notifi(month, day):
    today = json.dumps(datetime.date.today(), default=str).split(' ')[0]
    today_month = today.split('"',1)[1].split('-')[1]
    today_day = today.split('"',1)[1].split('-')[2]
    today_day = today_day.replace('\"','')

    res_m, res_d = compare_month(today_month,today_day,month,day)

    print("산책을 나간 지 {}달하고 {}일 지났습니다...!".format(res_m, res_d))
    print("강아지와 산책을 나가주세요..!")

def lambda_handler(event, context):
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()

    name = event.get('name')
    #쿼리문 작성
    sql = "select * from walk_info where dog_name='{}'".format(name)

    #작성한 쿼리문 실행
    curs.execute(sql)

    #쿼리문 실행 결과 rows에 저장
    rows = curs.fetchall()

    result = []
    #rows 값 result 배열에 삽입
    for row in rows:
        result.append(row)

    conn.close()

    new = json.dumps(result[-1][3], default=str).split(' ')[0]
    new = new.split('"',1)[1]
    month = new.split('-')[1]
    day = new.split('-')[2]

    return notifi(month, day)
