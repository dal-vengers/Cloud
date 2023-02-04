import sys
import logging
import pymysql
import os

def lambda_handler(event, context):
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()
    
    #변수 값 쿼리 작성
    sql = "INSERT INTO dog_info (regist_num,user_id,name,birth,weight,sex,kind_info_dog_kind) VALUES ('{}','{}','{}','{}',{},'{}','{}')".format(event['regist_num'],event['user_id'],event['name'],event['birth'],event['weight'],event['sex'],event['kind_info_dog_kind'])
   
    #작성한 쿼리문 실행
    curs.execute(sql)
    
    #RDS에 commit
    conn.commit()
    
    #RDS와 연결 종료료
    conn.close()
    return {
        'event':"success"
        }