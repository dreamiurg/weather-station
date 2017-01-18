import boto3
import logging

from weather.station import Station

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_dynamo_client():
    session = boto3.session.Session()
    client = session.client('dynamodb')
    return client


def create_response(response_code=200, body=None):
    response = {
        'statusCode': response_code,
    }
    if body is not None:
        response['body'] = body

    return response


def handler_get_latest_weather_report(event, context):
    client = get_dynamo_client()
    logger.info('event = {}, context = {}'.format(event, context))

    query = event.get('query')
    if query is None:
        return create_response(404)

    station = query.get('station')
    if station is None:
        return create_response(404)

    station = Station(client, station_name)
    latest_report = station.get_latest_report()
    if latest_report is None:
        return create_response(404)

    return create_response(200, {
        'station': station_name,
        'timestamp': latest_report.timestamp,
        'temperature': latest_report.temperature
    })
