import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
import datetime
import json
import pandas as pd

def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError('not JSON serializable')

def lambda_handler(event, context):

    #dynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    response = table.scan()

    current = datetime.datetime.now()
    current = current + datetime.timedelta(hours=9)
    json_data = json.dumps(current, default=json_default)

    if response['Count'] == 0:
        Index = 0

    else:
        show = response['Items']

        lines = pd.DataFrame(show)

        lines = lines.sort_values(by=['Index'], axis=0, ascending = True)
        lines = lines.reset_index(drop=True)

        Index = lines['Index'][len(lines)-1]+1


    table.put_item(
        Item={
            'Index' : Index,
            'device_name' : str(event['reported_id']),
            'date' : json_data,
            'lat' : str(event['reported_lat']),
            'lon' : str(event['reported_lon'])
        }
    )

    return None
