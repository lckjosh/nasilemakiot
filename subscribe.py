from rpi_lcd import LCD
import RPi.GPIO as GPIO
from gpiozero import LED, Button
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import random
from gpiozero import MCP3008
import datetime as datetime
import time
from time import sleep
import MFRC522
import telepot
import picamera
import sys
import os
import boto3
import botocore
import json

my_bot_token = '1481822767:AAGNnf8tFsKQ5LuxuTOah9gZpc9BTXYjVpc'
chat_id = '388290631'
host = "a1e7xdnu3fplgg-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "Certificates/AmazonRootCA1.pem"
certificatePath = "Certificates/cb51d7304a-certificate.pem.crt.txt"
privateKeyPath = "Certificates/cb51d7304a-private.pem.key"
my_rpi = AWSIoTMQTTClient("p1828034-client2")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
my_rpi.connect()

# bot variable
bot = telepot.Bot(my_bot_token)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(40, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
pwm = GPIO.PWM(11, 50)
pwm.start(0)

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(11, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(11, False)
    pwm.ChangeDutyCycle(0)

def unlockDoor():
    print("Door will be unlocked.")
    SetAngle(0)
    sleep(5)
    SetAngle(180)
    print("Door has been locked")

def manualUnlock(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    if message.payload == '1':
        unlockDoor()

def botUnlockDoor():
    unlockDoor()
    return "Door has been unlocked"


def respondToMsg(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Got command: {}'.format(command))
    print(chat_id)
    if command == '/unlock':
        message = {}
        message["deviceid"] = "deviceid_1828034"
        now = datetime.datetime.now()
        message["datetimeid"] = now.isoformat()
        message["rfid"] = 0
        message["camera"] = 0
        message["webcontrol"] = 0
        message["bot"] = 1
        message["servo"] = 1
        my_rpi.publish("lockdata", json.dumps(message), 1)
        bot.sendMessage(chat_id, botUnlockDoor())
        sleep(5)
        message = {}
        message["deviceid"] = "deviceid_1828034"
        now = datetime.datetime.now()
        message["datetimeid"] = now.isoformat()
        message["rfid"] = 0
        message["camera"] = 0
        message["webcontrol"] = 0
        message["bot"] = 0
        message["servo"] = 0
        my_rpi.publish("lockdata", json.dumps(message), 1)
    else:
        bot.sendMessage(
            chat_id, 'Unrecognised command, sorry but I only understand the /unlock command :(')

def uploadToS3(file_path, file_name, bucket_name):
    s3 = boto3.resource('s3')  # Create an S3 resource

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print("error bucket not found")

    # Upload the file
    full_path = file_path + "/" + file_name
    s3.Object(bucket_name, file_name).put(Body=open(full_path, 'rb'))
    print("File uploaded")

def addFace(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    if message.payload == '1':
        with picamera.PiCamera() as camera:
            now = datetime.datetime.now()
            timestring = now.isoformat()
            camera.capture(
                '/home/pi/assignment/pic/source_images/source_image_' + timestring + '.jpg')
        uploadToS3('/home/pi/assignment/pic/source_images', 'source_image_' + timestring + '.jpg', 'sp-p1828034-s3-bucket')

bot.message_loop(respondToMsg)
my_rpi.subscribe("webcontrol", 1, manualUnlock)
my_rpi.subscribe("addface", 1, addFace)
print('Listening for RPi commands...')
while True:
    time.sleep(10)
