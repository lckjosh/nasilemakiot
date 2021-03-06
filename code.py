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

my_bot_token = 'TELEGRAM_HTTP_API'
chat_id = 'CHAT_ID'
host = "REST_API_ENDPOINT"
rootCAPath = "ROOT_CA_PATH"
certificatePath = "CERTIFICATE_PATH"
privateKeyPath = "PRIVATE_KEY_PATH"
my_rpi = AWSIoTMQTTClient("ADMIN_NUMBER_CLIENT")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec
my_rpi.connect()

update = True
# card reading variables
uid = None
prev_uid = None
continue_reading = True
# lcd variable
lcd = LCD()
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


def compare_faces(source_image, target_image, similarity_threshold, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    try:
        response = rekognition.compare_faces(
            SimilarityThreshold=similarity_threshold,
            SourceImage={
                "S3Object": {
                    "Bucket": 'sp-p1828034-s3-bucket',
                    "Name": source_image
                }
            },
            TargetImage={
                "S3Object": {
                    "Bucket": 'sp-p1828034-s3-bucket',
                    "Name": target_image
                }
            }
        )
        for match in response['FaceMatches']:
            print("Target Face ({Confidence}%)".format(**match['Face']))
            print("  Similarity : {}%".format(match['Similarity']))
            return True
    except:
        return False
    return False


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


# Create an object of the class MFRC522
mfrc522 = MFRC522.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

# This loop keeps checking for chips.
# If one is near it will get the UID

while continue_reading:
    # Scan for cards
    (status, TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)

    # If a card is found
    if status == mfrc522.MI_OK:
        # Get the UID of the card
        (status, uid) = mfrc522.MFRC522_Anticoll()
        print(uid)
        # If card is the authorised card
        if uid == [136, 4, 93, 174, 127] or uid == [8, 138, 147, 144, 129]:
            message = {}
            message["deviceid"] = "deviceid_1828034"
            now = datetime.datetime.now()
            message["datetimeid"] = now.isoformat()
            message["rfid"] = 1
            message["servo"] = 1
            message["bot"] = 0
            message["camera"] = 0
            message["webcontrol"] = 0
            my_rpi.publish("lockdata", json.dumps(message), 1)
            lcd.text('Welcome', 1)
            lcd.text('Home!', 2)
            unlockDoor()
            lcd.clear()
            message = {}
            message["deviceid"] = "deviceid_1828034"
            now = datetime.datetime.now()
            message["datetimeid"] = now.isoformat()
            message["rfid"] = 0
            message["servo"] = 0
            message["bot"] = 0
            message["camera"] = 0
            message["webcontrol"] = 0
            my_rpi.publish("lockdata", json.dumps(message), 1)
        else:
            message = {}
            message["deviceid"] = "deviceid_1828034"
            now = datetime.datetime.now()
            message["datetimeid"] = now.isoformat()
            message["rfid"] = 2
            message["servo"] = 0
            message["bot"] = 0
            message["camera"] = 0
            message["webcontrol"] = 0
            my_rpi.publish("lockdata", json.dumps(message), 1)
            print('Unrecognised keycard!')
            print("UID of unrecognised card is {}".format(uid))
            lcd.text('Unrecognised', 1)
            lcd.text('Keycard!', 2)
            sleep(5)
            lcd.clear()
            message = {}
            message["deviceid"] = "deviceid_1828034"
            now = datetime.datetime.now()
            message["datetimeid"] = now.isoformat()
            message["rfid"] = 0
            message["servo"] = 0
            message["bot"] = 0
            message["camera"] = 0
            message["webcontrol"] = 0
            my_rpi.publish("lockdata", json.dumps(message), 1)
            with picamera.PiCamera() as camera:
                now = datetime.datetime.now()
                timestring = now.isoformat()
                camera.capture(
                    '/home/pi/assignment/pic/photo_' + timestring + '.jpg')
                bot.sendMessage(
                    chat_id, "Person with unrecognised Keycard has tried to enter your home! A photo of the person will be sent shortly..")
                bot.sendPhoto(chat_id, photo=open(
                    '/home/pi/assignment/pic/photo_' + timestring + '.jpg', 'rb'))
    # if button is pressed
    if GPIO.input(37) == GPIO.HIGH:
        GPIO.output(40, GPIO.HIGH)
        # picamera code
        with picamera.PiCamera() as camera:
            now = datetime.datetime.now()
            timestring = now.isoformat()
            camera.capture(
                '/home/pi/assignment/pic/photo_' + timestring + '.jpg')

            # # upload source image
            # for filename in os.listdir('/home/pi/assignment/pic/source_images'):
            #     uploadToS3('/home/pi/assignment/pic/source_images', filename,
            #                'sp-p1828034-s3-bucket')

            # upload target image
            uploadToS3('/home/pi/assignment/pic',
                       'photo_' + timestring + '.jpg', 'sp-p1828034-s3-bucket')

            # multi-user face recongition
            matched = False
            for filename in os.listdir('/home/pi/assignment/pic/source_images'):
                matched = compare_faces(
                    filename, 'photo_' + timestring + '.jpg', 95)
                if matched:
                    break
            if matched:
                # valid user unlock
                message = {}
                message["deviceid"] = "deviceid_1828034"
                now = datetime.datetime.now()
                message["datetimeid"] = now.isoformat()
                message["camera"] = 1
                message["servo"] = 1
                message["bot"] = 0
                message["rfid"] = 0
                message["webcontrol"] = 0
                my_rpi.publish("lockdata", json.dumps(message), 1)
                lcd.text('Welcome', 1)
                lcd.text('Home!', 2)
                unlockDoor()
                lcd.clear()
                message = {}
                message["deviceid"] = "deviceid_1828034"
                now = datetime.datetime.now()
                message["datetimeid"] = now.isoformat()
                message["camera"] = 0
                message["servo"] = 0
                message["bot"] = 0
                message["rfid"] = 0
                message["webcontrol"] = 0
                my_rpi.publish("lockdata", json.dumps(message), 1)
            else:
                message = {}
                message["deviceid"] = "deviceid_1828034"
                now = datetime.datetime.now()
                message["datetimeid"] = now.isoformat()
                message["camera"] = 2
                message["servo"] = 0
                message["bot"] = 0
                message["rfid"] = 0
                message["webcontrol"] = 0
                my_rpi.publish("lockdata", json.dumps(message), 1)
                lcd.text('Unrecognised', 1)
                lcd.text('Face!', 2)
                sleep(5)
                lcd.clear()
                message = {}
                message["deviceid"] = "deviceid_1828034"
                now = datetime.datetime.now()
                message["datetimeid"] = now.isoformat()
                message["camera"] = 0
                message["servo"] = 0
                message["bot"] = 0
                message["rfid"] = 0
                message["webcontrol"] = 0
                my_rpi.publish("lockdata", json.dumps(message), 1)
                bot.sendMessage(
                    chat_id, "Doorbell has been rung! A photo of the person at your door will be sent shortly..")
                bot.sendPhoto(chat_id, photo=open(
                    '/home/pi/assignment/pic/photo_' + timestring + '.jpg', 'rb'))
    if GPIO.input(37) == GPIO.LOW:
        GPIO.output(40, GPIO.LOW)
