# Bachelors-degree-project

This script is part of three-factor authentication system based on the use of Raspberry Pi microcomputer. Designed system allows to secure access to goods using three 
different forms of authorization. The keys used to secure the system are an RFID token, a numeric password and a randomly generated code sent in SMS message. 
Each authorized user has its own set of authentication keys that are validated when attempting to access the system. 
In case of entering wrong keys, system does not grant authorization, additionally, each authentication attempt is recorded for later control.


This repository contains script used in bachelor's degree project. Main scope is to manage all modules connected to Raspberry Pi and to display user interface with Tkinter.
User iterface is displayed on touch screen compatible with RPI. Project contains small databse in wchih all useres are saved. Structure of data base is as shown on photo below. 

![database](https://user-images.githubusercontent.com/44081987/152651519-f64c4ebc-3908-4ad8-b4fe-b0e52dd3f619.png)

Additionally, user pin code is saved in database as a result of hash function in order to secure most vulnerable data. 

User interface was projected with Tkinter library, it layout is simple due to fact that it has to show only important things like error informations, or inform user which authentication key is needed. 
Photo below shows project operation diagram, firstly user have to scan his personal RFID token, system will check if scanned token is assigned to person with access permissions. If condition is satisfied, on touch screen numeric keyboard will be displayed, in this step user have to insert his personal pin code. Provided code is hashed with special function and after this, it is compared to information saved in data base. If this step is completed, system enters last phase of authorization. Random numeric key is generated and sent with GSM module as a SMS message to user's mobilephone.
In this stage on touch display will be generated another numeric keyboard with label that informs user that sms code is needed. Access granted when satisfy all conditions.

![ProjectOperationDiagram](https://user-images.githubusercontent.com/44081987/152652160-13ef4ced-2b69-450f-80ff-d66f7f143f29.png)

Project was aswell created with specially projected chest to test modules and software. Photo below shows prototype in situation when user provided all needed keys and get access. 

![accessGranted](https://user-images.githubusercontent.com/44081987/152652735-98f5558c-9d86-4956-a801-7d2b5cf06f5d.png)

