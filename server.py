from flask import Flask, render_template, jsonify, request, Response, session, abort, flash, redirect, url_for
import os

import sys

import json
import numpy
import datetime
import decimal

# import gevent
# import gevent.monkey
# from gevent.pywsgi import WSGIServer
import time
from time import sleep


from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3
from boto3.dynamodb.conditions import Key, Attr

# set Web UI credentials
USERNAME = 'iot'
PASSWORD = '1qwer$#@!'

# gevent.monkey.patch_all()

host = "a1e7xdnu3fplgg-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "Certificates/AmazonRootCA1.pem"
certificatePath = "Certificates/cb51d7304a-certificate.pem.crt.txt"
privateKeyPath = "Certificates/cb51d7304a-private.pem.key"
my_rpi = AWSIoTMQTTClient("p1828034-server")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
my_rpi.connect()


class GenericEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def data_to_json(data):
    json_data = json.dumps(data, cls=GenericEncoder)
    return json_data


def connect_to_mysql(host, user, password, database):
    try:
        cnx = mysql.connector.connect(
            host=host, user=user, password=password, database=database)

        cursor = cnx.cursor()
        print("Successfully connected to database!")

        return cnx, cursor

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

        return None


def fetch_fromdb_as_json(cnx, cursor, sql):

    try:
        cursor.execute(sql)
        row_headers = [x[0] for x in cursor.description]
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers, result)))

        data_reversed = data[::-1]
        data = {'data': data_reversed}

        return data_to_json(data)

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None


def unlock():
    print("Door will be unlocked.")
    # SetAngle(0)
    message2 = {}
    message2["deviceid"] = "deviceid_1828034"
    now = datetime.datetime.now()
    message2["datetimeid"] = now.isoformat()
    message2["rfid"] = 0
    message2["camera"] = 0
    message2["bot"] = 0
    message2["webcontrol"] = 1
    message2["servo"] = 1
    my_rpi.publish("lockdata", json.dumps(message2), 1)
    my_rpi.publish("webcontrol", str(1), 1)
    sleep(5)
    # SetAngle(180)
    message2 = {}
    message2["deviceid"] = "deviceid_1828034"
    now = datetime.datetime.now()
    message2["datetimeid"] = now.isoformat()
    message2["rfid"] = 0
    message2["camera"] = 0
    message2["bot"] = 0
    message2["webcontrol"] = 0
    message2["servo"] = 0
    my_rpi.publish("lockdata", json.dumps(message2), 1)
    print("Door has been locked")

    return "Unlocked"


app = Flask(__name__)


@app.route("/api/getdata", methods=['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('LockTable')

            startdate = '2021'

            response = table.query(
                KeyConditionExpression=Key('deviceid').eq('deviceid_1828034')
                & Key('datetimeid').begins_with(startdate),
                ScanIndexForward=False
            )

            items = response['Items']

            n = 10  # limit to last 10 items
            data = items[:n]
            data_reversed = data[::-1]

            data = {'chart_data': data_to_json(data_reversed),
                    'title': "LockAI Data"}
            return jsonify(data)

        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


@app.route("/getRealTime", methods=['POST', 'GET'])
def getLight():
    if request.method == 'POST':
        try:
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('LockTable')

            startdate = '2021'

            response = table.query(
                KeyConditionExpression=Key('deviceid').eq('deviceid_1828034')
                & Key('datetimeid').begins_with(startdate),
                ScanIndexForward=False
            )

            items = response['Items']

            n = 1  # limit to last 10 items
            data = items[:n]
            data_reversed = data[::-1]

            return jsonify(data_to_json(data_reversed))
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route("/writeLOCK/<status>")
def writePin(status):
    if status == 'unlock':
        print("statusunlock")
        unlock()
    return render_template('index.html')


@app.route("/addFace")
def addFace():
    my_rpi.publish("addface", str(1), 1)
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == PASSWORD and request.form['username'] == USERNAME:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    try:
        print('Server waiting for requests')
        app.secret_key = os.urandom(12)
        # http_server = WSGIServer(('0.0.0.0', 8001), app)
        # app.debug = True
        # http_server.serve_forever()
        app.run(debug=True, port=8001, host="0.0.0.0")
    except:
        print("Exception")
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
