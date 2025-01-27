'''
This Flask application exposes a RESTful API for interfacing with a BMP280 sensor connected to an STM32 microcontroller. It manages:
    - Temperature: Reading and storing temperature values.
    - Pressure: Reading and storing pressure values.
'''

import serial

import json
from flask import Flask

from flask import jsonify
from flask import render_template
from flask import abort
from flask import request

app = Flask(__name__)


##########################
# Core application pages #
##########################
@app.route('/')
def hello_world():
    return jsonify({"message": 'Hello, World!'})

welcome = "Welcome to 3ESE API!"

@app.route('/api/welcome/')
def api_welcome():
    if request.method == 'GET' :
        return jsonify({"phrase" : welcome})

@app.route('/api/welcome/<int:index>', methods=['GET','POST','DELETE'])
def api_welcome_index(index):
    if index < 0 or index >= len(welcome):
        abort(404)

    if request.method == 'GET' :
        return jsonify({"index" : index, "value" : welcome[index]})

    #elif request.method == 'POST' :

    #return jsonify({"index": index, "val": welcome[index]})

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/api/request/', methods=['GET', 'POST'])
@app.route('/api/request/<path>', methods=['GET','POST'])
def api_request(path=None):
    resp = {
            "method":   request.method,
            "url" :  request.url,
            "path" : path,
            "args": request.args,
            "headers": dict(request.headers),
    }
    if request.method == 'POST':
        resp["POST"] = {
                "data" : request.get_json(),
                }
    return jsonify(resp)


################################
# Communication with the STM32 #
################################

SERIAL_BUFFER_SIZE = 10

tab_T = []  # Array for temperatures
tab_P = []  # Array for pressures

# To test with another device
ser = serial.Serial("/dev/ttyACM0",115200,timeout=1)
#ser = serial.Serial("/dev/ttyAMA0",115200,timeout=1)
ser.reset_output_buffer()
ser.reset_input_buffer()

def fill_serial_buffer(msg:str):
    if msg.__len__ < SERIAL_BUFFER_SIZE-2:
        return f"msg{' '*msg.__len__ - SERIAL_BUFFER_SIZE-2}"
    
    elif msg.__len__ > SERIAL_BUFFER_SIZE-2:
        return msg[:SERIAL_BUFFER_SIZE-2]
    else:
        return msg
    
# Temperature endpoint
@app.route('/api/temp/', methods=['GET', 'POST'])
def api_temp():
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    resp = {
        "method": request.method,
        "url": request.url,
        "args": request.args,
        "headers": dict(request.headers),
    }
    if request.method == 'POST':
        ser.write(b'GET_T   ')  # Sends to the STM32 that we want to perform a GET_T
        tempo = ser.readline().decode()  # Retrieve the value sent by the STM32
        tab_T.append(tempo[:9])  # Remove '\r\n' and add it to the array
        return jsonify(tab_T[-1])  # Return the last value
    if request.method == 'GET':
        return jsonify(tab_T)  # Return the entire temperature array

@app.route('/api/temp/<int:index>', methods=['GET', 'DELETE'])
def api_temp_index(index=None):
    resp = {
        "method": request.method,
        "url": request.url,
        "index": index,
        "args": request.args,
        "headers": dict(request.headers),
    }
    if request.method == 'GET':
        if index < len(tab_T):
            return jsonify(tab_T[index])  # Retrieve the value from the array at the index
        else:
            return jsonify("error: index out of range")
    if request.method == 'DELETE':
        if index < len(tab_T):
            return jsonify(f"The value {tab_T.pop(index)} has been removed")  # Remove value from the array
        else:
            return jsonify("error: index out of range")


# Pressure endpoint
@app.route('/api/pres/', methods=['GET', 'POST'])
def api_pres():
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    resp = {
        "method": request.method,
        "url": request.url,
        "args": request.args,
        "headers": dict(request.headers),
    }
    if request.method == 'POST':
        ser.write(b'GET_P   ')  # Sends to the STM32 that we want to perform a GET_P
        tempo = ser.readline().decode()  # Retrieve the value sent by the STM32
        tab_P.append(tempo[:20])  # Remove '\r\n' and add it to the array
        return jsonify(tab_P[-1])  # Return the last value
    if request.method == 'GET':
        return jsonify(tab_P)  # Return the entire pressure array

@app.route('/api/pres/<int:index>', methods=['GET', 'DELETE'])
def api_pres_index(index=None):
    resp = {
        "method": request.method,
        "url": request.url,
        "index": index,
        "args": request.args,
        "headers": dict(request.headers),
    }
    if request.method == 'GET':
        if index < len(tab_P):
            return jsonify(tab_P[index])  # Retrieve the value from the array at the index
        else:
            return jsonify("error: index out of range")
    if request.method == 'DELETE':
        if index < len(tab_P):
            return jsonify(f"The value {tab_P.pop(index)} has been removed")  # Remove value from the array
        else:
            return jsonify("error: index out of range")
            
