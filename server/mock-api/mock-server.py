from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/stations', methods = ['GET'])
def get_station_list():
    return jsonify({
        'body': {
            'stations' : ['one', 'two']
        }
    })

@app.route('/station/<station_name>', methods = ['GET'])
def get_station(station_name):
    return jsonify({
        'body': {
            'station': station_name,
            'timestamp': 123,
            'temerature': 75
        }
    })

app.run()
