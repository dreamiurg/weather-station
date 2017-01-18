import boto3
import arrow
from weather.station import StationManager

session = boto3.session.Session(profile_name='serverless')
client = session.client('dynamodb')

station_list = StationManager(client)

for station in station_list.get_stations():
    latest_report = station.get_latest_report()
    print('{} station last reported temperature of {} F on {}'.format(
        station.name, latest_report.temperature, arrow.get(latest_report.timestamp).format('YYYY-MM-DD HH:mm:ss')))
