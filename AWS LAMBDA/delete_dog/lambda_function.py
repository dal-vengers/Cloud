import sys
import logging
import pymysql
import os
import json

def lambda_handler(event, context):
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()

    #쿼리문 작성
    regist_num = event.get('regist_num')
    sql = "delete from dog_info where regist_num='{}'".format(regist_num)

    #작성한 쿼리문 실행
    curs.execute(sql)

    conn.commit()

    conn.close()
    return {
    }
