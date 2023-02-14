import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import pandas as pd
import haversine

def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(os.environ['TABLE_NAME'])

    response = table.query(
            KeyConditionExpression=Key('device_name').eq(event['reported_id'])
        )

    table2 = dynamodb.Table(os.environ['TABLE_NAME2'])

    response2 = table2.scan(
            FilterExpression=Attr('device_name').eq(event['reported_id'])
        )

    table3 = dynamodb.Table(os.environ['TABLE_NAME3'])

    response3 = table3.query(
            KeyConditionExpression=Key('device_name').eq(event['reported_id'])
        )

    show = response['Items'][0]

    cur_lat = float(show['lat'])
    cur_lon = float(show['lon'])

    cur_loc = (cur_lat, cur_lon)

    if response3['Count'] == 0:
        fin_dis = 0.00

    else:
        show2 = response2['Items']
        show3 = response3['Items'][0]

        lines = pd.DataFrame(show2)

        lines = lines.sort_values(by=['date'], axis=0, ascending = True)
        lines = lines.reset_index(drop=True)

        bef_loc = (float(lines['lat'][len(lines)-2]), float(lines['lon'][len(lines)-2]))

        dis = haversine.haversine(cur_loc, bef_loc, unit='km')

        cur_dis = float(show3['dis'])

        fin_dis = cur_dis + dis

    table3.put_item(
        Item={
            'device_name' : event['reported_id'],
            'dis' : str(fin_dis)
        }
    )
    return (cur_lat, cur_lon, fin_dis)
