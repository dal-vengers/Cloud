import boto3
import os
import pymysql
import json
import datetime
from boto3.dynamodb.conditions import Key, Attr

def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError('not JSON serializable')

def lambda_handler(event, context):

    conn = pymysql.connect(host=os.environ['host'], user=os.environ['user'], password=os.environ['password'], db=os.environ['db'])

    curs = conn.cursor()

    dynamodb = boto3.resource('dynamodb')

    # Get the dynamoDB table
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    response = table.query(
            KeyConditionExpression=Key('device_name').eq(str(event['reported_id']))
        )

    table1 = dynamodb.Table(os.environ['TABLE_NAME1'])

    response1 = table1.query(
            KeyConditionExpression=Key('device_name').eq(str(event['reported_id']))
        )

    dis = response1['Items'][0]
    item = response['Items'][0]

    current = datetime.datetime.now()
    current = current + datetime.timedelta(hours=9)

    json_data = json.dumps(current, default=json_default)

    walk_start_time = event['start_time']
    walk_end_time = json_data

    walk_start_time = datetime.datetime.strptime(walk_start_time, '%Y-%m-%d %H:%M:%S')
    walk_end_time = datetime.datetime.strptime(walk_end_time, '"%Y-%m-%d %H:%M:%S"')

    total_time = int((walk_end_time-walk_start_time).seconds/60)

    total_num_steps = item['vib']

    total_distance = round(float(dis['dis']), 1)

    sql = "INSERT INTO walk_info (regist_num,walk_start_time,walk_end_time,total_walk_time,distance,total_num_steps) VALUES ('{}','{}','{}',{},{},{})".format(event['regist_num'], walk_start_time, walk_end_time, total_time, total_distance, total_num_steps)

    #작성한 쿼리문 실행
    curs.execute(sql)

    #RDS에 commit
    conn.commit()

    #RDS와 연결 종료
    conn.close()

    sns = boto3.resource('sns')
    topic = sns.Topic(os.environ['SNS_ARN'])
    response = topic.publish(
        Message= event['regist_num']
    )

    return response
