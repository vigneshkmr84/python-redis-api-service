#from random import sample
from flask import Flask #, jsonify
from datetime import datetime
from flask.wrappers import Response
#from redisearch import Client, TextField, NumericField, Query
from redisearch import Client
import sys


import json, redis

#import redis


# Establishing Redis Connection 
connection = redis.Redis(host='localhost'
                         , charset='utf-8'
                         , decode_responses=True
                         , port=6379
                         , db=0)


app = Flask(__name__)
jsonElements = ['first_name', 'last_name', 'email', 'product', 'address', 'phone_number', 'count', 'cost', 'currency']

payload = {
            "name":"tom",
            "age": 23,
            "mobile": "444-123-4567"
          }

sample_user =   { "id": 1, "first_name": "Elaine", "last_name": "Dallosso", "email": "edallosso0@networkadvertising.org",
   "product": "Soup Campbells Beef With Veg", "address": "575 Portage Hill",
   "phone_number": "659-993-4818", "count": 17, "cost": 21.38, "currency": "USD" }


@app.route('/insert', methods=["GET"])
def insert():
    try:
        connection.mset({"car:0": "toyoto", "car:1": "BMW"})
        #connection.hmset('user:1', {'data': json.dumps(payload) });
        connection.hmset('user:1', sample_user);
        #.decode('utf-8')
        #print(map['product'])
        #map = json.loads(payload);
        #print(map['name'], map['age']);
        return Response('Inserted Successfully', status=201, mimetype='application/json')
    except:
        print('Exception Occurred during Insert')        
        return Response('Internal Server Error', status=500, mimetype='application/json')
    
    
@app.route("/get/all", methods=["GET"])
def getAll():
    print('Inside Get all Function', datetime.today())
    try:
        
        map=connection.hgetall('user:1')
        #print(map)
        #print(map['first_name']) 
        #print(json.loads(json.dumps(map)))
        #print(json.dumps(map))
        return Response(json.dumps(map), status=200, mimetype='application/json')
    except redis.RedisError:
        print('Exception occurred during retrieval')
        return Response('Internal Server Error', status=500, mimetype='application/json')
    
@app.route('/search', methods=['GET'])
def search():
    #print(sys.path)
    client = Client('users')
    res = client.search("Ela*")
    print(res)
    #raise Exception('Exception Check')
    return 'OK'


## Health Check API
@app.route("/health", methods=["GET"])
def health():
    print('Health Check @ ',  datetime.today())
    return Response('OK', status=200)

##### Custom Error Handling #####
@app.errorhandler(404)
def page_not_found(e):
    return Response('Page not Found', status=404, mimetype='application/json')
    
@app.errorhandler(500)
def page_not_found(e):
    return Response('Custom Internal Server Error', status=500, mimetype='application/json')


## initiating the server
if __name__ == '__main__':
    print("Starting service default port")
    app.run(host='0.0.0.0', debug=False)
    #app.run(host='0.0.0.0') # default - with debugger (will not show the custom Error pages)
    