import boto3
import botocore

LAST_REPORT_TABLE = 'weather_last'


class Base(object):
    def __init__(self, client):
        if not isinstance(client, botocore.client.BaseClient):
            raise AttributeError('Need boto client')
        self._client = client


class WeatherReport(object):
    def __init__(self, timestamp, temperature):
        self._timestamp = timestamp
        self._temperature = float(temperature)

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def temperature(self):
        return self._temperature


class Station(Base):
    def __init__(self, client, station_name):
        super(Station, self).__init__(client)
        self._station_name = station_name

    @property
    def name(self):
        return self._station_name

    def get_latest_report(self):
        response = self._client.get_item(
            TableName=LAST_REPORT_TABLE,
            Key={
                'station': {
                    'S': self._station_name,
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

        return WeatherReport(item['timestamp']['N'], item['temperature']['N'])


class StationManager(Base):
    def __init__(self, client):
        super(StationManager, self).__init__(client)

    def get_stations(self):
        response = self._client.scan(
            TableName=LAST_REPORT_TABLE,
            AttributesToGet=[
                'station'
            ],
        )

        items = response.get('Items')
        if items is None:
            return []

        station_list = [Station(self._client, item['station']['S']) for item in items]

        return station_list
