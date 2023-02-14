import sys
import logging
import pymysql
import os
def lambda_handler(event, context):
    #RDS와 연결
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()

    #앱 입력 값을 찾아서 변수로 지정

    #변수 값 쿼리 작성
    sql = "UPDATE dog_info SET name='{}', birth='{}', weight={}, sex='{}', kind_info_dog_kind='{}' WHERE regist_num='{}'".format(event['dog_name'],event['dog_birth'],event['dog_weight'],event['dog_gender'],event['dog_kind'],event['dog_rnum'])

    #작성한 쿼리문 실행
    curs.execute(sql)

    #RDS에 commit
    conn.commit()

    #RDS와 연결 종료
    conn.close()
    return {
        'event':event
        }
