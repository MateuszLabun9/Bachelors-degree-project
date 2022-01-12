from tkinter import *
import threading
import hashlib
from threading import Thread
import time
from time import sleep
from random import randint
import RPi.GPIO as GPIO
import serial
import mariadb
from mfrc522 import SimpleMFRC522


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, 1)
reader = SimpleMFRC522()


class Fullscreen_window:
    #Zmienne globalne użyte do poprawnego połączenia się z bazą danych
    global dbHost
    global dbName
    global dbUser
    global dbPass


    dbHost = 'localhost'
    dbName = 'db_data'
    dbUser = 'root'
    dbPass = 'password'

    def __init__(self):
        self.tk = Tk()
        self.tk.title("Three Factor Auth")#Ustawienie tytułu okna aplikacji
        self.mainframe = Frame(self.tk)#Utworzenie obiektu stanowiącego główną ramę
        self.tk.grid_rowconfigure(0, weight=1)#Konfiguracja wierszy siatki budującej okno aplikacji
        self.tk.grid_columnconfigure(0, weight=1)#Konfiguracja klumn siatki budującej okno aplikacji
        GPIO.output(18, 1)#GPIO 18 opowiada za połączenie Raspberry z przekaźnikiem 

        #self.tk.attributes('-zoomed', True)
        self.tk.attributes('-fullscreen', True)#Automatyczne powiększenie okna na cały ekran
        self.tk.bind("<Escape>", self.end_fullscreen)#Ustawienie przycisku Ecs w celu zmniejszenia okna
        self.tk.config(cursor="none")#Wyłączenie kursora
        self.showIdle()#Metoda wyświetlająca ekran startowy

        self.frame = Frame(self.tk, relief='sunken')
        self.frame.grid(sticky="we")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        t = Thread(target=self.rfid_detected, daemon=True)#Utworzenie nowej instancji Thread
        t.start()#Funckja rozpoczynająca wątek

    def showIdle(self):#Metoda wyświetlająca pierwszy raz ekran startowy
        self.welcomeLabel = Label(self.tk, text="Please Scan Your Token")#Ustawiwnie napisu informującego
        self.welcomeLabel.config(
            font='size, 20', justify='center', anchor='center')#Konfiguracja napisu
        self.welcomeLabel.grid(sticky=W+E, pady=210)

    def end_fullscreen(self, event=None):#Metoda odpowiedzialna za wyłączenie trybu pełnego ekranu
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def showIdle2(self):#Metoda wyświetlająca kolejny raz ekran startowy
        self.welcomeLabel = Label(self.tk, text="Please Scan Your Token")#Ustawiwnie napisu informującego
        self.welcomeLabel.config(#Konfiguracja napisu
            font='size, 20', justify='center', anchor='center')
        self.welcomeLabel.grid(sticky=W+E, pady=210)
        t = Thread(target=self.rfid_detected, daemon=True)#Ustawienie przerwania w momencie 
        t.start()#Rozpoczęcie nasłuchiwania

    def returnToIdleFromPinEntry(self):#Metoda wywołana po powrocie z metody pinEntry
        self.mainframe.pack_forget()
        self.showIdle2()

    def returnToIdleFromSMS(self):#Metoda wywołana po powrocie z etapu SMS
        self.SMSresultLabel.grid_forget()
        self.mainframe.grid_forget()
        GPIO.output(18, 1)#Zamknięcie zamka elektromagentycznego
        GPIO.cleanup()
        self.showIdle2()

    def returnToIdleWrongPin(self):#Metoda wywołana podczas błędnego wpisania kodu PIN
        self.PINresultLabel.grid_forget()
        self.mainframe.grid_forget()
        self.showIdle2()

    def rfid_detected(self):#Metoda wywoływana gdy token zostanie przyłożony do czytnika
        global accessLogId
        global pin
        id, text = reader.read()#Zapisanie do zmiennych danych odczytanych za pomocą czytnika RFID
        if id > 1000:
            mariadb_connection = mariadb.connect( #Połączenie się z bazą danych
                user=dbUser, passwd=dbPass, host=dbHost, port=3306, database=dbName)
            # Utworzenie kursora dzięki któremu możliwe jest zwracanie rekordów wierszowo
            cur = mariadb_connection.cursor(dictionary=True, buffered=True)
            cur.execute(#wykonanie polecenia SQL
                "SELECT * FROM access_list WHERE rfid_code = '%s'" % (id))
            userInfo = cur.fetchone() # zapisanie zwróconego  wiersza z bazy danych do zmiennej userInfo
            print(userInfo)
            if cur.rowcount != 1:#Sprawdzenie czy podany token jest zapisany w bazie danych
                
                cur.execute("INSERT INTO access_list SET rfid_code = '%s', is_enabled = 0" % (id))#Utworzenie w access_list kolejnego rekordu 
                cur2 = mariadb_connection.cursor(dictionary=True, buffered=True)#Utworzenie kolejnego kursora
                cur2.execute("SELECT * FROM access_list WHERE rfid_code = '%s'" % (id))
                new_user = cur2.fetchone()#Zapisanie danych pobranych z bazy do zmiennej
                new_id = new_user['user_id']
                cur.execute("INSERT INTO access_log SET  rfid_presented_datetime = NOW(),user_id = '%s', rfid_granted = 0" % ( new_id))
                mariadb_connection.commit()
                self.welcomeLabel.config(text="ACCESS DENIED")#Wyświetlenie napisu o braku dostępu
                time.sleep(3)
                self.welcomeLabel.grid_forget()
                self.frame.grid_forget()
                self.showIdle2()#Powrót do funkcji wyświetlającej główny ekran
            else:
                if userInfo['is_enabled']==0: #Sprawdzenie czy użytkownik posiada status is_enabled
                    cur.execute("INSERT INTO access_log SET  rfid_presented_datetime = NOW(),user_id = '%s', rfid_granted = 0" % ( userInfo['user_id']))
                    mariadb_connection.commit()
                    self.welcomeLabel.config(text="ACCESS DENIED")
                    time.sleep(3)
                    self.welcomeLabel.grid_forget()
                    self.frame.grid_forget()
                    self.showIdle2()
                elif userInfo['is_enabled']==1:#Jeśli is_enabled=1 uzytkownik posiada prawa dostępu
                
                    userPin = userInfo['pin']
                    self.welcomeLabel.grid_forget()
                    self.frame.grid_forget()

                    frame1 = Frame(self.mainframe)  

                    self.label1 = Label(frame1, text="Hello, %s!" % (
                        userInfo['name']),  font='size, 25', justify='center', anchor='center')#Utworzenie napisu
                    self.label1.grid(row=0, column=0, ipadx=5,
                                    ipady=5, padx=5, pady=5)
                    self.label1.grid_rowconfigure(1, weight=1)
                    self.label1.grid_columnconfigure(1, weight=1)

                    self.label2 = Label(
                        frame1, text="Please insert your pin code", font='size, 15')
                    self.label2.grid(row=2, column=0, ipadx=5,
                                    ipady=5, padx=5, pady=5)
                    self.label2.grid_rowconfigure(1, weight=1)
                    self.label2.grid_columnconfigure(1, weight=1)
                    frame1.grid(row=0, column=0)

                    pin = ''
                    frame2 = Frame(self.mainframe)  

                    keypad = [ # tablica zawierająca etykiety wszystkich przycisków
                        '1', '2', '3',
                        '4', '5', '6',
                        '7', '8', '9',
                        '', '0', '',
                    ]

                    r = 0 # zmienna odpowiadająca za ilość wierszy  
                    c = 0 # zmienna odpowiadająza za ilość kolumn

                    self.btn = list(range(len(keypad)))# utworzenie listy przycisków
                    for label in keypad:
                        Button(frame2, text=label, width=4, height=2, font='size, 20', command=lambda digitPressed=label: self.pinInput(
                            digitPressed, userPin, userInfo['sms_number'])).grid(row=r, column=c, ipadx=5, ipady=5, padx=2, pady=2)
                        c += 1 # iteracja kolumny
                        if c > 2:   # sprawdzenie czy indeks kolumny wynosi 2
                            c = 0 #jeśli tak, zmień kolumne na pierwszą od lewej
                            r += 1 # przejdz jeden wiersz niżej

                    frame1.grid(row=0, column=0)
                    frame2.grid(row=1, column=0)
                    self.mainframe.pack(expand=True)

                    self.RfidTimeout = threading.Timer(
                        30, self.returnToIdleFromPinEntry)#Rozpoczęcie timera, program oczekuje na wprowadzenie pinu
                    self.RfidTimeout.start()

                    self.WrongPinTimeout = threading.Timer(
                        5, self.returnToIdleWrongPin)#Rozpoczęcie timera odliczającego do powrotu na główny ekran
                    cur.execute("INSERT INTO access_log SET  rfid_presented_datetime = NOW(),user_id = '%s', rfid_granted = 1" % ( userInfo['user_id']) )
                    accessLogId=cur.lastrowid
                    mariadb_connection.commit()
            mariadb_connection.close()#Zamknięcie połęczenia z bazą danych

    def pinInput(self, value, userPin, mobileNumber):#Metoda sprawdzająca wpisany kod pin
        global accessLogId
        global pin
        global smsCodeEntered
        pin += value
        pinLength = len(pin)

        self.label2.config(text=pinLength * "*")
        if pinLength == 4:#Sprawdzenie czy długość wprowadzonego kodu pin wynosi 4
            encoded = pin.encode()
            encodedPin = hashlib.sha256(encoded).hexdigest()#Wykorzystanie funkcji haszującej 
            self.RfidTimeout.cancel()#Wyłączenie obsługi timera
            self.label1.destroy()
            self.label2.destroy()
            self.mainframe.pack_forget()# 

            if encodedPin == userPin:#Sprawdzenie czy podane hasło pin jest poprawne
                isGranted = 1 #Ustawienie flagi 
            else:
                isGranted = 0

            mariadb_connection2 = mariadb.connect(
                user=dbUser, passwd=dbPass, host=dbHost, port=3306, database=dbName)#Połączenie z bazą danych
            cur = mariadb_connection2.cursor(dictionary=True, buffered=True)
            cur.execute("UPDATE access_log SET  pin_entered_datetime = NOW(), pin_granted = %s WHERE access_id = %s" % ( isGranted, accessLogId))
            mariadb_connection2.commit()
            if encodedPin == userPin:#Jeżeli pin jest zgodny
                smsCode = self.sendSmsCode(mobileNumber)#Wywołanie metody wysyłającej kod SMS
                smsCodeEntered = ''
                frame3 = Frame(self.mainframe)  # , bg='#00008b'
                self.label3 = Label(frame3, text="Enter SMS code",
                                    font='size, 25', justify='center', anchor='center')
                self.label3.grid(row=0, column=0, ipadx=5,
                                 ipady=5, padx=5, pady=5)
                self.label3.grid_rowconfigure(1, weight=1)
                self.label3.grid_columnconfigure(1, weight=1)

                self.label4 = Label(
                    frame3, text="Please insert generated pin code", font='size, 15')
                self.label4.grid(row=2, column=0, ipadx=5,
                                 ipady=5, padx=5, pady=5)
                self.label4.grid_rowconfigure(1, weight=1)
                self.label4.grid_columnconfigure(1, weight=1)
                frame3.grid(row=0, column=0)

                frame2 = Frame(self.mainframe)  # , bg='#8B0000'
                keypad = [
                    '1', '2', '3',
                    '4', '5', '6',
                    '7', '8', '9',
                    '', '0', '',
                ]

                r = 0
                c = 0

                self.btn = list(range(len(keypad)))
                for label in keypad:
                    Button(frame2, text=label, width=4, height=2, font='size, 20', command=lambda digitPressed=label: self.smsCodeEnteredInput(
                        digitPressed, smsCode)).grid(row=r, column=c, ipadx=5, ipady=5, padx=2, pady=2)
                    c += 1
                    if c > 2:
                        c = 0
                        r += 1

                frame3.grid(row=0, column=0)
                frame2.grid(row=1, column=0)
                self.mainframe.pack(expand=True)

                self.SmsEntryTimeout = threading.Timer(
                    30, self.returnToIdleFromPinEntry)
                self.SmsEntryTimeout.start()
            else: #Jeżeli kod pin jest niezgodny
                self.PINresultLabel = Label(
                    self.tk, text="Incorrect PIN\nEntered!")
                self.PINresultLabel.config(
                    font='size, 20', justify='center', anchor='center')
                self.PINresultLabel.grid(sticky=W+E, pady=210)
                self.WrongPinTimeout.start()

    def smsCodeEnteredInput(self, value, smsCode):#Metoda sprawdzająca wpisany kod SMS
        global smsCodeEntered
        smsCodeEntered += value
        smsCodeEnteredLength = len(smsCodeEntered)

        self.label4.config(text=smsCodeEnteredLength * "*")
        if smsCodeEnteredLength == 4:#Sprawdzenie czy wpisany pin ma 4 cyfry
            if smsCodeEntered == smsCode:#Sprawdzenie poprawności pinu
                isSmsGranted = 1
            else:
                isSmsGranted = 0
            mariadb_connection = mariadb.connect(
                user=dbUser, passwd=dbPass, host=dbHost, port=3306, database=dbName)
            cur = mariadb_connection.cursor(dictionary=True, buffered=True)#Utworzenie połączenia z bazą danych
            cur.execute("UPDATE access_log SET smscode_entered_datetime = NOW(), smscode_granted = %s WHERE access_id = %s" % (isSmsGranted, accessLogId))
            mariadb_connection.commit()


            self.SmsEntryTimeout.cancel()
            self.label3.destroy()
            self.label4.destroy()
            self.mainframe.pack_forget()
            self.mainframe.grid_forget()
            if smsCodeEntered == smsCode:#Jeżeli wpisany kod SMS jest poprawny
                self.SMSresultLabel = Label(
                    self.tk, text="Thank You,\nAccess Granted")#Ustawienie napisu informującego
                self.SMSresultLabel.config(
                    font='size, 20', justify='center', anchor='center')
                self.SMSresultLabel.grid(columnspan=3, sticky=W+E, pady=210)
                GPIO.output(18, 0)#Otworzenie zamka elektromagnetycznego
                self.SmsEntryTimeout = threading.Timer(
                    30, self.returnToIdleFromSMS)#Rozpoczęcie timera powrotu do stanu początkowego
                self.SmsEntryTimeout.start()
            else:#Jeżeli podany kod SMS jest nieprawidłowy
                self.SMSresultLabel = Label(self.tk, text="Incorrect SMS Code")#informacja o niepoprawnym kodzie
                self.SMSresultLabel.config(
                    font='size, 20', justify='center', anchor='center')
                self.SMSresultLabel.grid(columnspan=3, sticky=W+E, pady=210)
                self.SmsEntryTimeout = threading.Timer(#Rozpoczęcie timera powrotu do stanu początkowego
                    10, self.returnToIdleFromSMS)
                self.SmsEntryTimeout.start()

    def sendSmsCode(self, mobilenumber):#Metoda wysyłająca kod SMS

        smsCode = str(randint(1000, 9999))#Generacja liczby losowej
        #Zawartość wiadomości SMS
        messageText = "Your access code is %s. Please enter this code on the touchscreen to continue." % smsCode
        port = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)#Konfiguracja portu szeregowego
        port.write(b"AT+CMGF=1\r")#Włączenie trybu tekstowego na tryb SMS
        time.sleep(3)
        command = "AT+CMGS=\""+mobilenumber+"\"\n"#Rozpoczęcie wysyłania widomości, podanie numeru odbiorcy
        port.write(str.encode(command))
        time.sleep(2)
        port.reset_output_buffer()#Wyczyszczenie bufora
        time.sleep(1)
        port.write(str.encode(messageText))
        port.write(str.encode(chr(26)))#Reprezentacja w kodzie ASCII kombinacji CTRL+Z
        return(smsCode)


if __name__ == '__main__':
    w = Fullscreen_window()
    w.tk.mainloop()
