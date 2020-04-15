from ipaddr import IPv4Network
from flask import Flask, request, abort, send_file
from datetime import datetime, timedelta

import redis
import json

import os
from dotenv import load_dotenv
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOT_ENV_PATH = os.path.join(BASE_DIR, '../.env')
STATIC_PATH = os.path.join(BASE_DIR, '../static/sticker.jpg')

if os.path.exists(DOT_ENV_PATH):
    load_dotenv(DOT_ENV_PATH)

app = Flask(__name__)

MASK = os.environ.get('MASK', '24')
LIMIT = int(os.environ.get('LIMIT', '100'))
INTERVAL = int(os.environ.get('INTERVAL', '60'))
TIMEOUT = int(os.environ.get('TIMEOUT', '120'))

REIDS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

red = redis.Redis(host=REIDS_HOST, port=REDIS_PORT, db=0)

@app.route('/', methods=['GET'])
def index():

    ip = request.headers.get('X-Forwarded-For')
    
    if ip == None:
        return '<h1>400 Bad Request</h1> <br> Expected X-Forwarded-For header', 400
    
    ip = ip[:15]

    net = str(IPv4Network(ip+'/'+MASK).network)
    
    net_obj = red.get(net)

    if net_obj:

        net_obj = json.loads(net_obj)

        if datetime.now() < datetime.fromtimestamp(net_obj['timeout']):
            abort(429)
        
        if datetime.now() > datetime.fromtimestamp(net_obj['first_req']) + timedelta(seconds=INTERVAL):
            new_net_obj(net)

        elif net_obj['req_count'] < LIMIT:
            net_obj['req_count']+=1
            red.set(net, json.dumps(net_obj))

        else:
            timeout = datetime.now() + timedelta(seconds=TIMEOUT)
            net_obj['timeout'] = timeout.timestamp()
            red.set(net, json.dumps(net_obj))
            abort(429)

    else:
        new_net_obj(net)

    return send_file(STATIC_PATH)


def new_net_obj(net):
    red.set(net, json.dumps({
        'first_req': datetime.now().timestamp(),
        'req_count': 1,
        'timeout': datetime.now().timestamp(),
    }))



if __name__ == '__main__':
    PORT = os.environ.get('PORT', '80')
    app.run(host='0.0.0.0', port=PORT, debug=True)