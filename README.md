# Bachelors-degree-project

This script is part of three-factor authentication system based on the use of Raspberry Pi microcomputer. Designed system allows to secure access to goods using three 
different forms of authorization. The keys used to secure the system are an RFID token, a numeric password and a randomly generated code sent in SMS message. 
Each authorized user has its own set of authentication keys that are validated when attempting to access the system. 
In case of entering wrong keys, system does not grant authorization, additionally, each authentication attempt is recorded for later control.

# Project structure

Main scope of this script is to manage all modules connected to Raspberry Pi and to display user interface projected with Tkinter library.
  - User interface is displayed on touch screen compatible with RPI and connected with DSI. 
  - MFRC522 module is used to scan RFID tokens and connect to Raspberry PI throught SPI interface. 
  - SIM800L is used to send one-time codes as a SMS message. UART interface and AT commands are used for communication between module and RPI.  

Project contains databse in which all useres are saved. Structure of data base is shown on photo below. There are two tables, access_list and access_log. First table contains list of all authorized users, second table contains history of all authorization attempts.

![database](https://user-images.githubusercontent.com/44081987/152651519-f64c4ebc-3908-4ad8-b4fe-b0e52dd3f619.png)

Additionally, user pin code is saved in database as a result of hash function in order to secure most vulnerable data. 


# User interface

User interface was projected with Tkinter library, layout is simple due to fact that it has to show only important things like error informations, or inform user which authentication key is needed. 
Photo below shows project operation diagram. Firstly user have to scan his personal RFID token, system will check if scanned token is assigned to person with access permissions. If condition is satisfied, on touch screen numeric keyboard will be displayed, in this step user have to insert his personal pin code. Provided code is hashed with special function and after that, it is compared to records saved in data base. If this step is completed, system enters last phase of authorization. Random numeric key is generated and sent with GSM module as a SMS message to user's mobilephone.
In this stage on touch display will be generated another numeric keyboard with label informing that sms code is needed. User have to provide received code via touchscreen. Access will be granted when user satisfy all conditions.

![ProjectOperationDiagram](https://user-images.githubusercontent.com/44081987/152652160-13ef4ced-2b69-450f-80ff-d66f7f143f29.png)

# Created prototype

In addition, prototype of project was created. It was built with wooden chest. When user get access, electomagnetic lock opens for 30 seonds.  Photo below shows prototype in situation when user provided all needed keys and get access. 

![accessGranted](https://user-images.githubusercontent.com/44081987/152652735-98f5558c-9d86-4956-a801-7d2b5cf06f5d.png)


# Error detection 

In case of providing incorrect data like providing unathorised data, on screen will be displayed suitable information

If scanned RFID tag is not connected to any authorized person saved in database, on screen will be displayed this information: 

![image](https://user-images.githubusercontent.com/44081987/153273935-869a64a6-cb96-42fc-b504-ae4295ce09b9.png)

If entered pin is incorrect on screen will be displayed this: 

![image](https://user-images.githubusercontent.com/44081987/153274093-cf86b1b2-2347-4dd1-8599-e8485b392a61.png)

Last error message will be displayed if user provide incorrect SMS code, in this situation: 

![image](https://user-images.githubusercontent.com/44081987/153274445-a4fe150a-55ba-49b5-8104-d931b45e41b3.png)

When error message occurs, system waits 5 seconds while displaying this information, after this time, system returns to main page
and waits for rescan of RFID token. 




