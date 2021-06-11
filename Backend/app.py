#!/usr/bin/python
import time
import os
import glob
import sys
import serial
import requests
import json
import collections
import functools
import operator
import subprocess
from RPi import GPIO
from threading import Thread
from datetime import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from werkzeug import datastructures
from werkzeug.datastructures import RequestCacheControl
from repositories.DataRepository import DataRepository


# Code voor Hardware
pins = [16, 12, 25, 24, 23, 26, 19, 13]
LCD_RS = 21
LCD_E = 20
solenoid = 22
buzzer_pin = 6

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

port = '/dev/ttyACM0'


def timer():
    sleep_duration = 5
    while sleep_duration > 0:
        print(f"you have {sleep_duration} seconds left")
        time.sleep(1)
        sleep_duration -= 1
    print("timer completed")
    # timer is complete
    print("locking again")
    # output locked
    msg = ""
    lock(msg)
    socketio.emit('B2F_lock', {'lock': '1'})


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


class LCD:
    def __init__(self, LCD_RS, LCD_E, pins):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.LCD_RS = LCD_RS
        self.LCD_E = LCD_E
        self.pins = pins
        GPIO.setup(self.LCD_E, GPIO.OUT)
        GPIO.setup(self.LCD_RS, GPIO.OUT)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.LCD_E, GPIO.HIGH)

    def send_instruction(self, value):
        GPIO.output(self.LCD_RS, GPIO.LOW)
        self.set_data_bits(value)

        GPIO.output(self.LCD_E, GPIO.LOW)
        time.sleep(0.002)
        GPIO.output(self.LCD_E, GPIO.HIGH)
        time.sleep(0.01)

    def send_character(self, character):
        GPIO.output(self.LCD_RS, GPIO.HIGH)
        self.set_data_bits(character)
        time.sleep(0.002)

        GPIO.output(self.LCD_E, GPIO.LOW)
        time.sleep(0.002)
        GPIO.output(self.LCD_E, GPIO.HIGH)
        time.sleep(0.01)

    def set_data_bits(self, value):
        mask = 0b00000001
        for index in range(0, 8):
            pin = self.pins[index]
            if (value & mask) == 0:
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)

            mask = mask << 1

    def init_LCD(self):
        self.send_instruction(0b00111000)
        self.send_instruction(0b00001111)
        self.send_instruction(0b00000001)
        self.clear_display()

    def write_message(self, message):
        for char in message[0:16]:
            self.send_character(ord(char))
        for char in message[16:]:
            self.move_screen()
            self.send_character(ord(char))
            time.sleep(0.5)

    def second_row(self, row=0, col=40):
        byte = row << 6 | col
        self.send_instruction(byte | 128)

    def move_screen(self):
        self.send_instruction(0b00011000)

    def clear_display(self):
        self.send_instruction(0b00000001)


def readSerial():
    ser = serial.Serial(port, 19200, timeout=0)
    while True:
        line = ser.readline().decode()
        time.sleep(0.1)
        if line != "":
            dict_barcode = barcode_lookup(line)
            print(dict_barcode)
            socketio.emit('B2F_scan', {'message': dict_barcode})


def barcode_lookup(line):
    json_data = open(
        '/home/student/2020-2021-projectone-freekherregods/Code/Backend/localJsonApi.json')
    localApi = json.load(json_data)
    barcode = line[:-1]

    for key in localApi:
        if key == barcode:
            name = localApi[barcode]['product_name']
            quantity = localApi[barcode]['product_quantity']
            categorie = localApi[barcode]['product_categorie']
            productid = localApi[barcode]['productid']
            dict_barcode = {}
            dict_barcode['name'] = name
            dict_barcode['quantity'] = quantity
            dict_barcode['line'] = line
            dict_barcode['categorie'] = categorie
            dict_barcode['productid'] = productid
    return dict_barcode


notes = {
    'B0': 31,
    'C1': 33, 'CS1': 35,
    'D1': 37, 'DS1': 39,
    'EB1': 39,
    'E1': 41,
    'F1': 44, 'FS1': 46,
    'G1': 49, 'GS1': 52,
    'A1': 55, 'AS1': 58,
    'BB1': 58,
    'B1': 62,
    'C2': 65, 'CS2': 69,
    'D2': 73, 'DS2': 78,
    'EB2': 78,
    'E2': 82,
    'F2': 87, 'FS2': 93,
    'G2': 98, 'GS2': 104,
    'A2': 110, 'AS2': 117,
    'BB2': 123,
    'B2': 123,
    'C3': 131, 'CS3': 139,
    'D3': 147, 'DS3': 156,
    'EB3': 156,
    'E3': 165,
    'F3': 175, 'FS3': 185,
    'G3': 196, 'GS3': 208,
    'A3': 220, 'AS3': 233,
    'BB3': 233,
    'B3': 247,
    'C4': 262, 'CS4': 277,
    'D4': 294, 'DS4': 311,
    'EB4': 311,
    'E4': 330,
    'F4': 349, 'FS4': 370,
    'G4': 392, 'GS4': 415,
    'A4': 440, 'AS4': 466,
    'BB4': 466,
    'B4': 494,
    'C5': 523, 'CS5': 554,
    'D5': 587, 'DS5': 622,
    'EB5': 622,
    'E5': 659,
    'F5': 698, 'FS5': 740,
    'G5': 784, 'GS5': 831,
    'A5': 880, 'AS5': 932,
    'BB5': 932,
    'B5': 988,
    'C6': 1047, 'CS6': 1109,
    'D6': 1175, 'DS6': 1245,
    'EB6': 1245,
    'E6': 1319,
    'F6': 1397, 'FS6': 1480,
    'G6': 1568, 'GS6': 1661,
    'A6': 1760, 'AS6': 1865,
    'BB6': 1865,
    'B6': 1976,
    'C7': 2093, 'CS7': 2217,
    'D7': 2349, 'DS7': 2489,
    'EB7': 2489,
    'E7': 2637,
    'F7': 2794, 'FS7': 2960,
    'G7': 3136, 'GS7': 3322,
    'A7': 3520, 'AS7': 3729,
    'BB7': 3729,
    'B7': 3951,
    'C8': 4186, 'CS8': 4435,
    'D8': 4699, 'DS8': 4978
}

popcorn_melody = [

    notes['A4'], notes['G4'], notes['A4'], notes['E4'], notes['C4'], notes['E4'], notes['A3'],
    notes['A4'], notes['G4'], notes['A4'], notes['E4'], notes['C4'], notes['E4'], notes['A3'],

    notes['A4'], notes['B4'], notes['C5'], notes['B4'], notes['C5'], notes['A4'], notes['B4'], notes['A4'], notes['B4'], notes['G4'],
    notes['A4'], notes['G4'], notes['A4'], notes['F4'], notes['A4'],


    notes['A4'], notes['G4'], notes['A4'], notes['E4'], notes['C4'], notes['E4'], notes['A3'],
    notes['A4'], notes['G4'], notes['A4'], notes['E4'], notes['C4'], notes['E4'], notes['A3'],

    notes['A4'], notes['B4'], notes['C5'], notes['B4'], notes['C5'], notes['A4'], notes['B4'], notes['A4'], notes['B4'], notes['G4'],
    notes['A4'], notes['G4'], notes['A4'], notes['B4'], notes['C5'],

    notes['E5'], notes['D5'], notes['E5'], notes['C5'], notes['G4'], notes['C5'], notes['E4'],
    notes['E5'], notes['D5'], notes['E5'], notes['C5'], notes['G4'], notes['C5'], notes['E4'],

    notes['E5'], notes['FS5'], notes['G5'], notes['FS5'], notes['G5'], notes['E5'], notes['FS5'], notes['E5'], notes['FS5'], notes['D5'],
    notes['E5'], notes['D5'], notes['E5'], notes['C5'], notes['E5'],

    ###

    notes['E5'], notes['D5'], notes['E5'], notes['C5'], notes['G4'], notes['C5'], notes['E4'],
    notes['E5'], notes['D5'], notes['E5'], notes['C5'], notes['G4'], notes['C5'], notes['E4'],

    notes['E5'], notes['FS5'], notes['G5'], notes['FS5'], notes['G5'], notes['E5'], notes['FS5'], notes['E5'], notes['FS5'], notes['D5'],
    notes['E5'], notes['D5'], notes['B4'], notes['D5'], notes['E5'],
]
popcorn_tempo = [
    8, 8, 8, 8, 8, 8, 4,
    8, 8, 8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 4,
    8, 8, 8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 4,
    8, 8, 8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 4,
    8, 8, 8, 8, 8, 8, 4,

    8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 4,
]

# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


print("**** Program started ****")

# API ENDPOINTS


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

# routes


@app.route('/producten', methods=['GET'])
def read_producten():
    if request.method == 'GET':
        return jsonify(product=DataRepository.read_producten()), 200
    return None


@app.route('/producten', methods=['DELETE'])
def remove_product(productid):
    if request.method == 'DELETE':
        data = DataRepository.delete_product(productid)
        if data > 0:
            return jsonify(status="success", row_count=data), 201
        else:
            return jsonify(status="no update", row_count=data), 201


@app.route('/slot', methods=['GET'])
def read_slot():
    if request.method == 'GET':
        return jsonify(product=DataRepository.read_meting_by_device(4)), 200
    return None


@socketio.on('connect')
def initial_connection():
    print('A new client connect')


@app.route('/temperatuur')
def show_temp():
    temp = DataRepository.read_meting_by_action(3)
    return jsonify(temperatuur=temp), 200


@app.route('/historiek')
def show_historiek():
    return jsonify(historiek=DataRepository.read_historiek()), 200


@app.route('/producten')
def show_producten():
    return jsonify(producten=DataRepository.read_producten()), 200


@app.route('/chartdata')
def show_chart():
    graph_data = DataRepository.read_graph_data()
    list_categories = []
    list_tijdstippen = []
    list_hoeveelheden = []
    dict_hoeveelheid_categorie = {}
    counter = 0
    for data in graph_data:
        categorie = data['categorie']
        tijdstip = data['tijdstip']
        hoeveelheid = data['hoeveelheid']
        list_categories.append(categorie)
        list_tijdstippen.append(tijdstip)
        list_hoeveelheden.append(hoeveelheid)
        if(categorie in dict_hoeveelheid_categorie):
            cat = categorie + str(counter)
            dict_hoeveelheid_categorie[cat] = hoeveelheid
            counter += 1
        dict_hoeveelheid_categorie[categorie] = hoeveelheid

    water = 0
    frisdrank = 0
    melk = 0
    fruitsap = 0
    alcohol = 0
    for x in dict_hoeveelheid_categorie:
        if "water" in x:
            water += dict_hoeveelheid_categorie[x]
        if "melk" in x:
            melk += dict_hoeveelheid_categorie[x]
        if "frisdrank" in x:
            frisdrank += dict_hoeveelheid_categorie[x]
        if "fruitsap" in x:
            fruitsap += dict_hoeveelheid_categorie[x]
        if "alcohol" in x:
            alcohol += dict_hoeveelheid_categorie[x]
    dict_hoeveelheid_categorie.clear()
    if water != 0:
        dict_hoeveelheid_categorie['water'] = water
    if frisdrank != 0:
        dict_hoeveelheid_categorie['frisdrank'] = frisdrank
    if melk != 0:
        dict_hoeveelheid_categorie['melk'] = melk
    if fruitsap != 0:
        dict_hoeveelheid_categorie['fruitsap'] = fruitsap
    if alcohol != 0:
        dict_hoeveelheid_categorie['alcohol'] = alcohol

    if len(list_hoeveelheden) != 0:
        total, result = 0, []
        for i in range(0, len(list_hoeveelheden)):
            result.append(list_hoeveelheden[i] + total)
            total += list_hoeveelheden[i]

    else:
        result = []

    sorted_dict = dict(sorted(dict_hoeveelheid_categorie.items()))
    values = list(sorted_dict.values())
    list_categories = list(dict.fromkeys(list_categories))
    dict_result = {}
    dict_result['uniek_cat'] = sorted(list_categories)
    dict_result['tijdstip'] = list_tijdstippen
    dict_result['hoeveelheden'] = result
    dict_result['hoeveelheid_cat'] = values
    return jsonify(message=dict_result), 200


@socketio.on('F2B_inscan')
def inscan(msg):
    print(msg)
    dict_barcode = {}
    dict_barcode = msg['barcode']['message']
    print(dict_barcode)
    add_product(dict_barcode)


@socketio.on('F2B_uitscan')
def uitscan(msg):
    dict_barcode = {}
    dict_barcode = msg['barcode']['message']
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    DataRepository.delete_product(dict_barcode['productid'])
    DataRepository.add_meting(formatted_date, dict_barcode['name'],
                              "uitgescand", None, 2, dict_barcode['productid'])


@ socketio.on('F2B_lock')
def lock(msg):
    print("lock")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(solenoid, GPIO.OUT)
    GPIO.output(solenoid, 0)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    DataRepository.add_meting(formatted_date, bool(True),
                              "slot aan", 4, 6, None)


@ socketio.on('F2B_unlock')
def unlock(msg):
    print("unlock")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(solenoid, GPIO.OUT)
    GPIO.output(solenoid, 1)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    DataRepository.add_meting(formatted_date, bool(False),
                              "slot uit", 4, 7, None)
    timer_thread = Thread(target=timer)
    timer_thread.start()


@ socketio.on('F2B_shutdown')
def shutdown(msg):
    os.system("sudo poweroff")


def add_product(dict_barcode):
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    DataRepository.add_product(dict_barcode['productid'])
    DataRepository.add_meting(formatted_date, dict_barcode['name'],
                              "ingescand", None, 1, dict_barcode['productid'])


def get_temp():
    counter = 0
    while True:
        temperatuurmeting = round(read_temp(), 1)
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        DataRepository.add_meting(
            formatted_date, temperatuurmeting, "temp-meting", 1, 3, None)
        temperatuur = DataRepository.read_meting_by_action(3)
        #lcd = LCD(LCD_RS, LCD_E, pins)
        # lcd.second_row()
        # lcd.write_message(temperatuur.get("waarde"))
        # lcd.send_character(32)
        # lcd.send_character(0xDF)
        # lcd.send_character(67)
        print(temperatuur.get("waarde"))
        counter += 1
        print(counter)
        if counter % 3 == 0:
            DataRepository.maintenance(3)
            counter = 0
        time.sleep(5)


def my_callback(channel):
    t3 = Thread(target=doorBuzzer)
    t3.setDaemon(True)
    t3.start()


def doorBuzzer():
    start = time.perf_counter()
    if GPIO.input(27) == 0:
        for i in range(0, 15):
            if GPIO.input(27) == 1:
                break
            end = time.perf_counter()
            elapsed = end - start
            print(elapsed)
            time.sleep(1)
            if(round(elapsed) >= 10):
                print("buzzzzz")
                play(popcorn_melody, popcorn_tempo, 0.50, 1.000)

    else:
        pass


def buzz(frequency, length):  # create the function "buzz" and feed it the pitch and duration)

    if(frequency == 0):
        time.sleep(length)
        return
    # in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    period = 1.0 / frequency
    delayValue = period / 2  # calcuate the time for half of the wave
    # the number of waves to produce is the duration times the frequency
    numCycles = int(length * frequency)

    for i in range(numCycles):  # start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(buzzer_pin, True)  # set pin 27 to high
        time.sleep(delayValue)  # wait with pin 27 high
        GPIO.output(buzzer_pin, False)  # set pin 27 to low
        time.sleep(delayValue)  # wait with pin 27 low


def play(melody, tempo, pause, pace=0.800):

    for i in range(0, len(melody)):		# Play song
        if(GPIO.input(27) == 1):
            break
        noteDuration = pace/tempo[i]
        # Change the frequency along the song note
        buzz(melody[i], noteDuration)
        pauseBetweenNotes = noteDuration * pause
        time.sleep(pauseBetweenNotes)


lcd = LCD(LCD_RS, LCD_E, pins)
lcd.init_LCD()
lcd.init_LCD()
IP = subprocess.check_output(["hostname", "-I"]).split()[0]
ip = str(IP).split("'")
# lcd.write_message("temperatuur:")
lcd.write_message("IP")
lcd.second_row()
lcd.write_message(ip[1])
t1 = Thread(target=get_temp)
t2 = Thread(target=readSerial)
t1.setDaemon(True)
t2.setDaemon(True)
t1.start()
t2.start()

GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(
    27, GPIO.BOTH, callback=my_callback, bouncetime=200)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
