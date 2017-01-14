import boto3

session = boto3.session.Session(profile_name='serverless')
client = session.client('dynamodb')

response = client.get_item(
    TableName='weather_last',
    Key={
        'station': {
            'S': 'chip-1-real',
        }
    },
    AttributesToGet=[
        'temperature',
        'timestamp'
    ],
)

print response['Item']