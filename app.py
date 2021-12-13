#from random import sample
from flask import Flask, request #, jsonify
from datetime import datetime
from flask.wrappers import Response
from types import SimpleNamespace
from collections import namedtuple

from redisearch import Client, TextField, NumericField, Query
#from redisearch import Client
import json, redis


NOT_AVAILABLE = 'API Not found'
SERVER_ERROR = 'Internal Server Error'


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
        #connection.hmset('user:1', {'data': json.dumps(payload) });
        connection.hmset('user:1', sample_user)
        return Response('Inserted Successfully', status=201, mimetype='application/json')
    except:
        print('Exception Occurred during Insert')        
        return Response(SERVER_ERROR, status=500, mimetype='application/json')
    
    # implement service name as the api input
    # also add the hset insert to the respective 2nd key  
@app.route('/post', methods=['POST'])    
def post():
    rawRequst = request.json
    id = rawRequst['id']
    requestBody = json.dumps(rawRequst)
    
    #jsonData = json.loads(requestBody,object_hook=lambda d : namedtuple('X', d.keys()) (*d.values()))
    #print(jsonData.firstName)
    #print(jsonData.lastName)

    try:
        key='test_user:' + str(id)    
        connection.hmset(key, rawRequst)
        return Response('Inserted Successfully', status=201, mimetype='application/json')
    except redis.RedisError:
        print('Exception occured')
        return Response(SERVER_ERROR, status=500, mimetype='application/json')


@app.route('/get/all', methods=['GET'])
def getAll():
    print('Inside Get all Function', datetime.today())
    try:
        map=connection.hgetall('user:*')
        #print(map)
        #print(map['first_name']) 
        #print(json.loads(json.dumps(map)))
        #print(json.dumps(map))
        return Response(json.dumps(map), status=200, mimetype='application/json')
    except redis.RedisError:
        print('Exception occurred during retrieval')
        return Response(SERVER_ERROR, status=500, mimetype='application/json')
    
@app.route('/search', methods=['GET'])
def search():
    #print(sys.path)
    print(request.args['query'])
    
    client = Client('users')
    res = client.search('Ela*')
    #print(res)
    #raise Exception('Exception Check')
    print('Total elements in result - ', res.total)
    jsonObject = []
    for element in range(res.total):
        #print(res.docs[element])
        e = res.docs[element]
        parser(e)
        #print(str(res.docs[element]).replace('Document ',''))
        #jsonvalues = json.dumps(str(res.docs[element]).replace('Document ','').replace('\'', '\"').replace('None', 'null'))
        jsonObject[element]=json.dumps(str(res.docs[element]).replace('Document ','').replace('\'', '\"').replace('None', 'null'))
    #return json.dumps(res)
    #print(json.loads(jsonvalues))
    return Response(json.loads(jsonObject), status=200, mimetype='application/json' )

def parser(e):
    print(e.first_name)
    
    return 0;
    
## Health Check API
@app.route('/health', methods=['GET'])
def health():
    print('Health Check @ ',  datetime.today())
    return Response('OK', status=200)

##### Custom Error Handling #####

@app.errorhandler(404)
def page_not_found(e):
    return Response(NOT_AVAILABLE, status=404, mimetype='application/json')
    
@app.errorhandler(500)
def page_not_found(e):
    return Response(SERVER_ERROR, status=500, mimetype='application/json')


## initiating the server
if __name__ == '__main__':
    print('Starting service default port')
    #app.run(host='0.0.0.0', debug=False)
    app.run(host='0.0.0.0') # default - with debugger (will not show the custom Error pages)
    