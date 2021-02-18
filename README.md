## ST0324 Internet of Things
## CA2 Public Tutorial
## Team Nasi Lemak
### Members:
Lim Choong Kai Joshua  (1828034)  
Foo Han  (1828274)
  
# LockAI
# Section 1
## Overview of project
What is the application about?  
The application is a Smart Locck that seeks to make securing the front door of every home more convenient. The target audience would be for owners of households who would like to have a convenient Smart Lock and for people who are looking to upgrade their traditional key locks into something that is much more easy to use. This application can be integrated into a smart home environment by combining its usage with other IoT smart home devices.


How does the final RPI set-up looks like?




How does the web or mobile application look like?
Provide at least one screenshot of your web app, and more if your web app consists of more than 1 page. Otherwise, I will assume your webapp only can show 1 page.  Label your screenshots so that they may be referenced in Section F.


		


System architecture of our system














Evidence that we have met basic requirements

Provide bullet list to describe how your group has met basic requirements

Requirement
Evidence
Used three sensors
Used RFID Card Reader, PiCamera, Button 
Used MQTT
Our MQTT endpoint --> 
Example of data sent through MQTT : 
Stored data in cloud
Stored locking-related data in DynamoDB database in AWS Cloud
Used cloud service
Use AWS Rekognition to detect faces and unlock the lock based on the faces uploaded, hosted web server on EC2, used DynamoDB
Provide real-time sensor value / status
Show the real-time value of RFID Card Reader unlock status, PiCamera unlock status.
Provide historical sensor value/ status
Show historical value of RFID Card Reader unlocks and attempts history, PiCamera unlocks and attempts history
Control actuator
Placed button on webpage to control Servo Motor.

Bonus features on top of basic requirements

Provide bullet list of the bonus features you have added on top of basic requirements

Login system for the web interface
Telegram bot to alert user regarding doorbell being rung and to alert user if an unrecognised keycard or face has been used to try to unlock the Smart Lock
Implementation of AWS Rekognition which detects whether the human in frame is indeed an authorised person
Added a button on the web page to allow admin user to add in a face to the list of recognised users
Program is able to have many different authorised users instead of just one.

Quick-start guide (Readme first)

Give a few lines of basic instructions on how I need to run your app, e.g

First connect hardware as in Section 2
Run the server.py on the EC2 instance for web server
Run the code.py file and subscribe.py on the Raspberry PI

Section 2
Hardware requirements 

a.Hardware checklist

Raspberry PI
PiCamera
Buzzer
Servo Motor
RFID Card Reader and Cards
LCD Screen
Button
Breadboard

b. Hardware setup instructions

Describe any special setup instructions here
Connection for Servo Motor:


Connection for RFID Reader:


Connections for LCD Screen:

GPIO Pins:
ServoMotor: GPIO17
Button: GPIO26
LED: GPIO21



c. Fritzing Diagram

Paste a Fritzing diagram of your setup here

You can get the Fritzing software at Blackboard Labs folder (third link from top)



Section 3
Software Requirements



Software checklist

If your applications needs the user to install additional Python or other libraries, pleasse provide here. A simple one like this is sufficient. 

Telepot library
boto3
botocore
AWKIoTPythonSDK
paho-mqtt
awscli
MFRC522.py


Software setup instructions

Install the needed dependencies on the Raspberry Pi with the following command:

sudo pip install AWSIoTPythonSDK paho-mqtt awscli botocore boto3

Register your Raspberry Pi as a thing by following the instructions below:
On the left navigation pane of the AWS Educate IoT Core console, click Manage, Things, then click Create on the new page that appears.

Click “Create a single thing”
Enter “MyRaspberryPi” in the Name section and click Next.
Click “One-click certification creation”
Download the three certificates, the click on the link to download the root CA for AWS IoT. Choose the Root CA1 to download.



Store these 4 files in a safe location that you will remember as we will need to use them later. 
On the left navigation pane of the AWS Educate IoT Core console, click Secure, Policies, then click “Create” at the top right of the page.
Enter the following details:

Click “Create”.
On the left navigation pane of the AWS Educate IoT Core console, click Secure, Certificates.
The certificate you created in step 6 is shown. 
Click the three dots to the right of your certificate, click “Attach policy”, then check the box next to your security policy and click “Attach”.

Click the three dots to the right of your certificate, click “Attach thing”, then check the box next to your thing and click “Attach”.
On the left navigation pane of the AWS Educate IoT Core console, click Manage, Things.
Click on “MyRaspberryPi”, then click “Interact”.

Copy the Rest API Endpoint into a text file and save it somewhere you remember as we will need to use it later.
Go to AWS IAM and click “Roles” under “Access management”. 
Click “Create role”, then select “IoT” under use case.

Click “Next: Permissions”, then click “Next: Tage”, then click “Next: Review”.
Enter “IoTLockAI” under Role Name, then click “Create role”. 
Go to AWS DynamoDB, and on the left navigation pane click “Tables”.
Click “Create table”.
Fill in the fields accordingly:

Click “Create”.
On the left navigation pane of the AWS Educate IoT Core console, click Act, Rules, then click “Create” at the top right of the page.
Enter lockdataRule in the Name field, and under Rule Query Statement enter SELECT * FROM ‘lockdata’
Under “Set one of more actions”, click “Add action”. 
Click “Split message into multiple columns of a DynamoDB table (DynamoDBv2)”, then click “Configure action” below.
Under “Table name”, select the table you created in step 25. Select the role you created in step 22, then click “Update role”.
Click “Add action”.
On the next page, scroll down and click “Create role”. 
On the next page, click on the three dots next to your newly created rule, then click “Enable”. 
Go to AWS S3, then click “Create bucket”.
Type in a unique name for your bucket. In our case we have chosen “sp-p1828034-s3-bucket”. Ensure that the “AWS Region” is set to “us-east-1”. Click “Create” at the bottom of the page. 
Go to AWS EC2 and click on “Launch Instance”. 
Select the “Amazon Linux 2” VM:

Accept the default instance type of “t2.micro” and click “Next: Configure Instance Details”.
Change “Auto-assign Public IP” to “Enable”. Click “Next: Add Storage”, then click “Next: Add Tags”. 
Click “Add Tag”, enter “Name” under “Key” and “Python Web Server” under “Value”. Click “Next: Configure Security Group”. 
Select “Create a new security group”. Enter “WebServerSG” as the Security Group name and “Security group for Web Server” as the Description. 
Click “Add Rule”, select “Custom TCP”, enter “8001” under Port and “Anywhere” under Source. Click “Save rules”. 
Click “Review and Launch”, then click “Launch” on the next page. 
Create a new key pair and specify the name as “Keypair for Python web server”. 
Click “Download Key Pair” and save the file in a location you remember as we will need to use it later. 
Use WinSCP and PuTTY to connect to the EC2 instance. The username for the EC2 instance is “ec2-user”. Use the keyfile in step 46 to authenticate. 
Run the following commands in the EC2 instance to install Python 3.8:
sudo yum check-update
sudo yum install -y amazon-linux-extras
sudo amazon-linux-extras enable python3.8
sudo yum clean metadata
sudo yum install python38 -y
Run the following commands in the EC2 instance to set the timezone to Singapore:
sudo nano /etc/sysconfig/clock
Locate the ZONE entry, and change it to the time zone file, in this case:
ZONE=”Singapore”
Save the file and exit the editor.
sudo ln -sf /usr/share/zoneinfo/Singapore /etc/localtime
sudo reboot
Run the following command in the EC2 instance to install needed dependencies:
sudo pip install boto3 flask numpy AWSIoTPythonSDK
Create a Telegram bot by starting a chat with BotFather and following the instructions shown below, replacing the username of the bot with something of your own:

Save the HTTP API given in a safe location you remember as we will need to use it later on. 




Section 5
Modify Codes and Directory Structure

Create a folder called “assignment”. This folder will be transferred to the home folder of the Raspberry Pi.
Place the certificates downloaded in Section 3 step 8 in “assignment/Certificates”
In “code.py”, “server.py”, and “subscribe.py”, replace these lines accordingly with the file paths of your certificates:

In “code.py” and “subscribe.py”, replace “TELEGRAM_HTTP_API” with the HTTP API in Section 4 step 52. 
In “server.py”, replace the credentials at the top of the file with that of your choosing.
Directory structure of the “assignment” folder should be as follows:

Transfer the “assignment” folder to the home folder of the Raspberry Pi. 
Run the “code.py” file once by running  python code.py , then send a message to your telegram bot created in Section 4 step 51. 
Get the chat_id from the terminal in the Raspberry Pi running “code.py” and replace “CHAT_ID” in “code.py” and “subscribe.py” with it. 
Replace all references of “sp-p1828034-s3-bucket” with your bucket name created in Section 4 step 36. 

Section 6 
Run Program

Run “code.py” and “subscribe.py” on the Raspberry Pi 
Transfer the “assignment” folder to the home folder of the EC2 instance
Run the following commands on the EC2 instance:
python3.8 -m venv ~/assignment/env
source ~/assignment/env/bin/activate
cd ~/assignment
pip3 install boto3 flask numpy
python3.8 server.py
Navigate to port 8001 of your EC2 instance. The Public IPv4 DNS can be found at AWS EC2, Instances, Click on your instance ID:
 
Log in with your credentials in Section 5 step 5.
Point the Picamera at your face and click “Add Face” in the top right hand corner of the web interface to add yourself as a valid user for facial recognition.
Have fun!

Section 7
Task List


A table listing members names and the parts of the assignment they worked on


Name of member
Part of project worked on
Contribution percentage
Lim Choong Kai Joshua
Set up GitHub repository for documentation and code collaboration
Store image captured in AWS S3
Use AWS Rekognition to compare current face with stored valid users’ face to unlock door
Upgraded Web Interface to show real-time state of lock
Host web interface on AWS EC2
Add valid user’s face from web interface
Updated all codes to match with AWS (e.g. remove local database)
Video Editing
Step by step tutorial Sections 3 to 6
Documentation for system architecture


60%
Foo Han
MQTT publishing of lock data from Pi to AWS
Store lock data in AWS DynamoDB
Use Buzzer as doorbell
Show real-time input from RFID scanner and Picamera in web interface
Show historical values of RFID scanner, Picamera and Telegram bot data for unlocking and locking
Create AWS IoT Rules, Topics, and relevant permissions
Documentation for hardware setup



40%



Section 7
References


https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff

https://docs.aws.amazon.com/rekognition/latest/dg/API_CompareFaces.html

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html



-- End of CA2 Step-by-step tutorial --

