import json
import logging
import random
import time

import click as click
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

MQTT_QOS_LEVEL = 0
MQTT_TOPIC = 'station/data'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

logger = None


def configure_logging(verbose):
    global logger
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def get_mqtt_client(endpoint, root_ca, cert, key, ws, client_id):
    client = None
    if ws:
        logging.debug('Creating MQTT+Websockets client using endpoint %s:443', endpoint)
        client = AWSIoTMQTTClient(client_id, useWebsocket=True)
        client.configureEndpoint(endpoint, 443)
        client.configureCredentials(root_ca)
    else:
        logging.debug('Creating MQTT+TCP client using endpoint %s:8883', endpoint)
        client = AWSIoTMQTTClient(client_id)
        client.configureEndpoint(endpoint, 8883)
        client.configureCredentials(root_ca, key, cert)

    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    client.connect()

    return client


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--endpoint', '-e', help='AWS IoT endpoint domain name.', required=True)
@click.option('--root-ca', '-r', help='Root CA file path.', type=click.Path(exists=True), required=True)
@click.option('--cert', '-c', help='Certificate file path.', type=click.Path(exists=True), required=True)
@click.option('--key', '-k', help='Private key file path.', type=click.Path(exists=True), required=True)
@click.option('--client-id', '-i', help='MQTT client ID.', default='weather-station', show_default=True)
@click.option('--ws', help='Use MQTT over WebSocket.', is_flag=True, default=False)
@click.option('--verbose', '-v', help='Print debugging information.', is_flag=True)
@click.pass_context
def cli(ctx, endpoint, root_ca, cert, key, ws, client_id, verbose):
    """Welcome to weather station"""
    configure_logging(verbose)
    mqtt_client = get_mqtt_client(endpoint, root_ca, cert, key, ws, client_id)
    ctx.obj['mqtt_client'] = mqtt_client


@cli.command(short_help='Generate fake data samples and publish them to AWS IoT topic.')
@click.option('--samples', '-s', type=int, default=10, help='How many fake data samples to generate.', show_default=True)
@click.option('--delay', '-d', type=float, default=1, help='Delay between sending each sensor reading, seconds.', show_default=True)
@click.pass_context
def samples(ctx, samples, delay):
    """Generate fake data samples and send them to AWS IoT."""
    mqtt_client = ctx.obj['mqtt_client']

    logger.info('Generating %d fake data samples with %s second(s) delay between', samples, delay)

    samples_sent = 0
    while samples_sent < samples:
        samples_sent += 1

        payload = {'station': mqtt_client._mqttCore.getClientID(), 'timestamp': time.time(), 'temperature': random.uniform(65, 75)}
        payload_str = json.dumps(payload)

        mqtt_client.publish(MQTT_TOPIC, payload_str, MQTT_QOS_LEVEL)

        logger.info('Published sample data point {}/{} to topic [{}] ({})'.format(samples_sent, samples, MQTT_TOPIC, payload_str))
        time.sleep(delay)


@cli.command(short_help='Read sensor data and publish them to AWS IoT topic.')
@click.option('--delay', '-d', type=float, default=1, help='Delay between sending each sensor reading, seconds.', show_default=True)
@click.pass_context
def run(ctx, delay):
    """Generate fake data samples and send them to AWS IoT."""
    mqtt_client = ctx.obj['mqtt_client']

    logger.info('Reading data from sensor every %d second(s)', delay)

    from w1thermsensor import W1ThermSensor
    therm_sensor = W1ThermSensor()

    while True:
        temperature = therm_sensor.get_temperature(W1ThermSensor.DEGREES_F)
        payload = get_payload(mqtt_client, temperature)
        payload_str = json.dumps(payload)

        mqtt_client.publish(MQTT_TOPIC, payload_str, MQTT_QOS_LEVEL)

        logger.info('Published data point to topic [{}] ({})'.format(MQTT_TOPIC, payload_str))
        time.sleep(delay)


def get_payload(mqtt_client, temperature):
    return {
        'station': mqtt_client._mqttCore.getClientID(),
        'timestamp': time.time(),
        'temperature': temperature
    }


if __name__ == '__main__':
    cli(obj={})
