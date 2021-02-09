from rpi_lcd import LCD
import RPi.GPIO as GPIO
from gpiozero import LED, Button
import time
from time import sleep
import mysql.connector
import MFRC522
import signal
import telepot
import picamera
import sys
import os
import boto3
import botocore

my_bot_token = '1481822767:AAGNnf8tFsKQ5LuxuTOah9gZpc9BTXYjVpc'
chat_id = '388290631'
u = 'lockuser'
pw = 'lockpass'
h = 'localhost'
db = 'lockdatabase'
cnx = mysql.connector.connect(user=u, password=pw, host=h, database=db)
cursor = cnx.cursor()
print("Successfully connected to database!")
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

while update:
    def SetAngle(angle):
        duty = angle / 18 + 2
        GPIO.output(11, True)
        pwm.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(11, False)
        pwm.ChangeDutyCycle(0)

    def unlockDoor():
        print("Door will be unlocked.")
        # SetAngle(0)
        # sleep(3)
        # SetAngle(180)
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
            bot.sendMessage(chat_id, botUnlockDoor())
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

    bot.message_loop(respondToMsg)
    print('Listening for RPi commands...')

    # Capture SIGINT for cleanup when the script is aborted
    def end_read(signal, frame):
        global continue_reading
        print("Ctrl+C captured, ending read.")
        continue_reading = False
        pwm.stop()
        GPIO.cleanup()

    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

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
                i = 1
                sql = "INSERT INTO lockdata (locking) VALUES (%(val)s)"
                cursor.execute(sql, {'val': i})
                cnx.commit()
                lcd.text('Welcome', 1)
                lcd.text('Home!', 2)
                sleep(1)
                lcd.clear()
                unlockDoor()
            else:
                i = 0
                sql = "INSERT INTO lockdata (locking) VALUES (%(val)s)"
                cursor.execute(sql, {'val': i})
                cnx.commit()
                print('Unrecognised keycard!')
                print("UID of unrecognised card is {}".format(uid))
                lcd.text('Unrecognised', 1)
                lcd.text('Keycard!', 2)
                sleep(3)
                lcd.clear()
                with picamera.PiCamera() as camera:
                    timestring = time.strftime(
                        "%Y-%m-%dT%H:%M:%S", time.gmtime())
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
                timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
                camera.capture(
                    '/home/pi/assignment/pic/photo_' + timestring + '.jpg')

                # upload source image
                for filename in os.listdir('/home/pi/assignment/pic/source_images'):
                    uploadToS3('/home/pi/assignment/pic/source_images', filename,
                           'sp-p1828034-s3-bucket')

                # upload target image
                uploadToS3('/home/pi/assignment/pic',
                           'photo_' + timestring + '.jpg', 'sp-p1828034-s3-bucket')
                
                # multi-user face recongition
                matched = False
                for filename in os.listdir('/home/pi/assignment/pic/source_images'):
                    matched = compare_faces(filename, 'photo_' + timestring + '.jpg', 95)
                    if matched:
                        break
                if matched:
                    # valid user unlock
                    lcd.text('Welcome', 1)
                    lcd.text('Home!', 2)
                    sleep(1)
                    lcd.clear()
                    unlockDoor()
                else:
                    lcd.text('Unrecognised', 1)
                    lcd.text('Face!', 2)
                    sleep(3)
                    lcd.clear()
                    bot.sendMessage(chat_id, "Doorbell has been rung! A photo of the person at your door will be sent shortly..")
                    bot.sendPhoto(chat_id, photo = open('/home/pi/assignment/pic/photo_' +timestring+ '.jpg', 'rb'))
        if GPIO.input(37) == GPIO.LOW:
            GPIO.output(40, GPIO.LOW)

# except KeyboardInterrupt:
#     print('Interrupted')
#     pwm.stop()
#     GPIO.cleanup()
#     try:
#         sys.exit(0)
#     except SystemExit:
#         os._exit(0)


#     # pwm.stop()
#     # GPIO.cleanup()
