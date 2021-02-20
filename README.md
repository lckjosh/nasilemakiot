## ST0324 Internet of Things
## CA2 Public Tutorial
## Team Nasi Lemak
### Members:
Lim Choong Kai Joshua  (1828034)  
Foo Han  (1828274)

# LockAI
# Section 1 - Overview of project
## What is LockAI?  
LockAI is a Smart Lock that seeks to make securing the front door of every home more convenient. The target audience would be for owners of households who would like to have a convenient Smart Lock and for people who are looking to upgrade their traditional key locks into something that is much more easy to use. This application can be integrated into a smart home environment by combining its usage with other IoT smart home devices.


## Final RPI Set-up:

![Alt text](README-images/hardware_setup.png?raw=true)

## Web Application Screenshots:  

![Alt text](README-images/login_web_interface.png?raw=true)  

![Alt text](README-images/web_interface.png?raw=true)

## System architecture:  

![Alt text](README-images/sys_archi.png?raw=true)


# Section 2 Hardware requirements 
## Hardware checklist
- Raspberry Pi
- PiCamera
- Buzzer
- Servo Motor
- RFID Card Reader and Cards
- LCD Screen
- Button
- Breadboard

## Hardware setup instructions
### Connection for Servo Motor:

![Alt text](README-images/servo_connection.png?raw=true)


### Connection for RFID Reader:

![Alt text](README-images/rfid_connection.png?raw=true)



### Connections for LCD Screen:

![Alt text](README-images/lcd_connection.png?raw=true)

GPIO Pins:  
- ServoMotor: GPIO17  
- Button: GPIO26  
- LED: GPIO21  



## Fritzing Diagram

![Alt text](README-images/fritzing.png?raw=true)


# Section 3 - Software Requirements
## Software Checklist

- Telepot library
- boto3
- botocore
- AWKIoTPythonSDK
- paho-mqtt
- awscli

## Software Setup Instructions
### Install Dependencies
1. Install the needed dependencies on the Raspberry Pi with the following command:
```
sudo pip install AWSIoTPythonSDK paho-mqtt awscli botocore boto3 telepot
```

### Create a 'Thing'
2. Register your Raspberry Pi as a thing by following the instructions below:

3. On the left navigation pane of the AWS Educate IoT Core console, click Manage, Things, then click Create on the new page that appears.

4. Click "Create a single thing"

5. Enter "MyRaspberryPi" in the Name section and click Next.

6. Click "One-click certification creation"

7. Download the three certificates, the click on the link to download the root CA for AWS IoT. Choose the Root CA1 to download.

    ![Alt text](README-images/certificates.png?raw=true)

    ![Alt text](README-images/rootca.png?raw=true)

8. Store these 4 files in a safe location that you will remember as we will need to use them later. 

9. On the left navigation pane of the AWS Educate IoT Core console, click Secure, Policies, then click "Create" at the top right of the page.

10. Enter the following details:

    ![Alt text](README-images/security_policy.png?raw=true)

11. Click "Create".

12. On the left navigation pane of the AWS Educate IoT Core console, click Secure, Certificates.

13. The certificate you created in step 6 is shown. 

14. Click the three dots to the right of your certificate, click "Attach policy", then check the box next to your security policy and click "Attach".

    ![Alt text](README-images/attach_policy_to_cert.png?raw=true)

15. Click the three dots to the right of your certificate, click "Attach thing", then check the box next to your thing and click "Attach".

16. On the left navigation pane of the AWS Educate IoT Core console, click Manage, Things.

17. Click on "MyRaspberryPi", then click "Interact".

    ![Alt text](README-images/rest_api_endpoint.png?raw=true)

18. Copy the Rest API Endpoint into a text file and save it somewhere you remember as we will need to use it later.

### Create a Role
19. Go to AWS IAM and click "Roles" under "Access management". 

20. Click "Create role", then select "IoT" under use case.

    ![Alt text](README-images/iot_use_case.png?raw=true)

21. Click "Next: Permissions", then click "Next: Tage", then click "Next: Review".

22. Enter "IoTLockAI" under Role Name, then click "Create role". 

### Create DynamoDB Table
23. Go to AWS DynamoDB, and on the left navigation pane click "Tables".

24. Click "Create table".

25. Fill in the fields accordingly:

    ![Alt text](README-images/create_dynamodb.png?raw=true)

26. Click "Create".

### Create a Rule
27. On the left navigation pane of the AWS Educate IoT Core console, click Act, Rules, then click "Create" at the top right of the page.

28. Enter lockdataRule in the Name field, and under Rule Query Statement enter `SELECT * FROM 'lockdata'`

29. Under "Set one of more actions", click "Add action". 

30. Click "Split message into multiple columns of a DynamoDB table (DynamoDBv2)", then click "Configure action" below.

31. Under "Table name", select the table you created in step 25. Select the role you created in step 22, then click "Update role".

32. Click "Add action".

33. On the next page, scroll down and click "Create role". 

34. On the next page, click on the three dots next to your newly created rule, then click "Enable". 

### Set up AWS S3
35. Go to AWS S3, then click "Create bucket".

36. Type in a unique name for your bucket. In our case we have chosen "sp-p1828034-s3-bucket". Ensure that the "AWS Region" is set to "us-east-1". Click "Create" at the bottom of the page. 

### Set up AWS EC2 Instance
37. Go to AWS EC2 and click on "Launch Instance". 

38. Select the "Amazon Linux 2" VM:

    ![Alt text](README-images/ami.png?raw=true)

39. Accept the default instance type of "t2.micro" and click "Next: Configure Instance Details".

40. Change "Auto-assign Public IP" to "Enable". Click "Next: Add Storage", then click "Next: Add Tags". 

41. Click "Add Tag", enter "Name" under "Key" and "Python Web Server" under "Value". Click "Next: Configure Security Group". 

42. Select "Create a new security group". Enter "WebServerSG" as the Security Group name and "Security group for Web Server" as the Description. 

43. Click "Add Rule", select "Custom TCP", enter "8001" under Port and "Anywhere" under Source. Click "Save rules". 

44. Click "Review and Launch", then click "Launch" on the next page. 

45. Create a new key pair and specify the name as "Keypair for Python web server". 

46. Click "Download Key Pair" and save the file in a location you remember as we will need to use it later. 

47. Use WinSCP and PuTTY to connect to the EC2 instance. The username for the EC2 instance is "ec2-user". Use the keyfile in step 46 to authenticate. 

48. Run the following commands in the EC2 instance to install Python 3.8:

```
sudo yum check-update
sudo yum install -y amazon-linux-extras
sudo amazon-linux-extras enable python3.8
sudo yum clean metadata
sudo yum install python38 -y
```
49. Run the following commands in the EC2 instance to set the timezone to Singapore:
```
sudo nano /etc/sysconfig/clock
```
Locate the ZONE entry, and change it to the time zone file, in this case:
```
ZONE="Singapore"
```
Save the file and exit the editor.
```
sudo ln -sf /usr/share/zoneinfo/Singapore /etc/localtime
sudo reboot
```
50. Run the following command in the EC2 instance to install needed dependencies:
```
sudo pip install boto3 flask numpy AWSIoTPythonSDK
```

### Set up Telegram Bot
51. Create a Telegram bot by starting a chat with BotFather and following the instructions shown below, replacing the username of the bot with something of your own:

    ![Alt text](README-images/botfather.png?raw=true)

52. Save the HTTP API given in a safe location you remember as we will need to use it later on. 


# Section 4 - Modify Codes and Directory Structure

1. Create a folder called "assignment". This folder will be transferred to the home folder of the Raspberry Pi.

2. Place the certificates downloaded in Section 3 step 8 in "assignment/Certificates"

3. In "code.py", "server.py", and "subscribe.py", replace these lines accordingly with the file paths of your certificates and the text of your Rest API Endpoint in Section 3 step 18:

    ![Alt text](README-images/replace_certs.png?raw=true)

4. In "code.py" and "subscribe.py", replace "TELEGRAM_HTTP_API" with the HTTP API in Section 3 step 52. 
5. In "server.py", replace the credentials at the top of the file with that of your choosing.

6. Directory structure of the "assignment" folder should be as follows:

    ![Alt text](README-images/directory_structure.png?raw=true)

7. Transfer the "assignment" folder to the home folder of the Raspberry Pi. 

8. Run the "code.py" file once by running  python code.py , then send a message to your telegram bot created in Section 3 step 51. 

9. Get the chat_id from the terminal in the Raspberry Pi running "code.py" and replace "CHAT_ID" in "code.py" and "subscribe.py" with it. 

10. Replace all references of "sp-p1828034-s3-bucket" with your bucket name created in Section 3 step 36. 

# Section 5 - Run Program

1. Login to your AWS Educate account and click on “Account Details”.

2. Click “Show” beside AWS CLI:

    ![Alt text](README-images/aws_cli_show.png?raw=true)

3. Copy the credentials given to your clipboard:

    ![Alt text](README-images/aws_credentials.png?raw=true)

4. On both the Raspberry Pi and the EC2 instance, run the following commands:
```
rm ~/.aws/credentials
nano ~/.aws/credentials
```
Paste the credentials into the editor and press Ctrl-O and then Ctrl-X to save.

5. Run "code.py" and "subscribe.py" on the Raspberry Pi 

6. Transfer the "assignment" folder to the home folder of the EC2 instance

7. Run the following commands on the EC2 instance:
```
python3.8 -m venv ~/assignment/env
source ~/assignment/env/bin/activate
cd ~/assignment
pip3 install boto3 flask numpy AWSIoTPythonSDK
python3.8 server.py
```

8. Navigate to port 8001 of your EC2 instance. The Public IPv4 DNS can be found at AWS EC2, Instances, Click on your instance ID:

![Alt text](README-images/public_dns_ec2.png?raw=true)
 
9. Log in with your credentials in Section 4 step 5.

10. Point the Picamera at your face and click "Add Face" in the top right hand corner of the web interface to add yourself as a valid user for facial recognition.

11. The telegram bot will send you notifications and can be used to control the lock as shown below:

![Alt text](README-images/telegraminterface.png?raw=true)

12. Have fun!

# Section 6 - References
https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff

https://docs.aws.amazon.com/rekognition/latest/dg/API_CompareFaces.html

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html
