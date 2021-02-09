from flask import Flask, render_template, jsonify, request,Response

import mysql.connector
import sys
import signal

import json
import numpy
import datetime
import decimal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
from rpi_lcd import LCD
import time
from time import sleep
import RPi.GPIO as GPIO

gevent.monkey.patch_all()


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
    json_data = json.dumps(data,cls=GenericEncoder)
    return json_data

def connect_to_mysql(host,user,password,database):
    try:
        cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)

        cursor = cnx.cursor()
        print("Successfully connected to database!")

        return cnx,cursor

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

        return None

def fetch_fromdb_as_json(cnx,cursor,sql):
    
    try:
        cursor.execute(sql)
        row_headers=[x[0] for x in cursor.description] 
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers,result)))
        
        data_reversed = data[::-1]

        data = {'data':data_reversed}

        return data_to_json(data)

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
pwm=GPIO.PWM(11, 50)
pwm.start(0)

def SetAngle(angle):
    print("hellokenneth")
    duty = angle / 18 + 2
    GPIO.output(11, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(11, False)
    pwm.ChangeDutyCycle(0)
    print("hellokenneth")

def unlock():
    print("helloprint")
    SetAngle(0)
    sleep(3)
    SetAngle(180)
    return "unlock"

def lock():
    SetAngle(180)
    return "lock"


app = Flask(__name__)

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            host='localhost'; user='lockuser'; password='lockpass'; database='lockdatabase';
            sql="SELECT * FROM lockdata ORDER BY datetimeinfo DESC LIMIT 10"
            cnx,cursor = connect_to_mysql(host,user,password,database)
            json_data = fetch_fromdb_as_json(cnx,cursor,sql)
            loaded_r = json.loads(json_data)
            data = {'chart_data': loaded_r, 'title': "IOT Data"}
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

@app.route("/")
def chartsimple():
    return render_template('index.html')

@app.route("/writeLOCK/<status>")
def writePin(status):
    if status == 'unlock':
        print("statusunlock")
        response = unlock()
    else:
        response = lock()

    return response

if __name__ == '__main__':
   try:
        print('Server waiting for requests')
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        http_server.serve_forever()
   except:
        print("Exception")
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

