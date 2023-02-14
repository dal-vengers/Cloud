import boto3
import os
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):

    #dynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    table.put_item(
        Item={
            'device_name' : event['reported_id'],
            'lat' : str(event['reported_lat']),
            'lon' : str(event['reported_lon']),
            'vib' : int(event['reported_vib'])
        }
    )

    return None
