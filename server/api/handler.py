import json
import boto3

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_dynamo_client():
    session = boto3.session.Session()
    client = session.client('dynamodb')
    return client

def create_response(response_code=200, body=None):
    response = {
        "statusCode": response_code,
        "body": json.dumps(body)
    }
    return response

def get_latest_weather(client, station_name):
    response = client.get_item(
    TableName='weather_last',
        Key={
            'station': {
                'S': station_name,
            }
        },
        AttributesToGet=[
            'temperature',
            'timestamp'
        ],
    )

    item = response.get('Item')
    if item is None:
        return None

    return {
        'station': station_name,
        'timestamp': item['timestamp']['N'],
        'temperature': item['temperature']['N']
    }


def handler_get_latest_weather(event, context):
    client = get_dynamo_client()
    logger.info('event = {}, context = {}'.format(event, context))

    station_name = event.get('station')
    if station is None:
        return create_response(404)

    body = get_latest_weather(client, station_name)
    if body is None:
        return create_response(404)

    return create_response(200, body)

