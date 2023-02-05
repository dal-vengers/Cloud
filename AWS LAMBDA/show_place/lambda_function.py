import json
import os
import pymysql
import urllib.parse
def lambda_handler(event, context):
    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])
    curs = conn.cursor()
    
    place_type = urllib.parse.unquote(event.get('type'))

    sql = "select place_name,place_address, place_lat, place_lng from place_info where FIND_IN_SET(place_type,'{}')".format(place_type)
    curs.execute(sql)
    rows = curs.fetchall()
    
    result=[]
    for row in rows:
        result.append(row)

    return {
        'result': result,
        'event':event
    }
    