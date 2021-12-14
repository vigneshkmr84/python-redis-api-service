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
INVALID_ARGUMENTS = 'Invalid Arguments Passed'


USER_KEY_PREFIX = 'user:'
TOTAL_KEYS = 'total'

# Establishing Redis Connection 
connection = redis.Redis(host='localhost'
                         , charset='utf=8'
                         , decode_responses=True
                         , port=6379
                         , db=0)


app = Flask(__name__)
#jsonElements = ['first_name', 'last_name', 'email', 'product', 'address', 'phone_number', 'count', 'cost', 'currency']

@app.route('/insert', methods=['POST'])
def insert():
    rawRequst = request.json
    id = rawRequst['id']
    status=""
    service_name=""
    try:
        status = request.args.get('status')
        service_name = request.args.get('serviceName')
        #print(service_name)
        #print(status)
    except ValueError:
        print(INVALID_ARGUMENTS)
        return Response(INVALID_ARGUMENTS, status=400, mimetype='application/json')
            
    #requestBody = json.dumps(rawRequst)

    try:
        # inserting raw data into the hash set
        key=USER_KEY_PREFIX + str(id)    
        connection.hmset(key, rawRequst)
        
        # maintain status of each id per service level (success:s1 /  failure:s1, success:s2 / failure:s2 etc. ) 
        service_status_key=status + ":" + service_name        
        connection.sadd(service_status_key, id)
        
        # maintain total SET of all incominng keys (irrespective of the service it comes from)
        connection.sadd(TOTAL_KEYS, id)
        
        return Response('Inserted Successfully', status=201, mimetype='application/json')
    except redis.RedisError:
        print('Exception occured')
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
    query=request.args.get('query')
    print("Query = ", query)
    
    client = Client('users')
    #res = client.search('Olimpia')
    res = client.search(query)
    #print("Response ")
    #print(res)
    #raise Exception('Exception Check')
    print('Total elements in result = ', res.total)
    #print(type(res))
    #print(res)
    print("==============================================================================")
    jsonArray = []
    
    for element in range(res.total):
        #print(res.docs[element])
        e = res.docs[element]
        #print(e)
        print("------------------------------------------------------------------------------")
        #print(e.id)
        
        document_string = str(e)
        json_string = document_string.replace('Document', '').replace('\'', '\"').replace('None', 'null')
        
        #prints string in double quotes("")
        #print(json_string)
        jsondata = json.loads(json_string)
        #print(jsondata.last_name)
        
        #print(type(e.id))
        
        print(jsondata)
        
        jsonArray.append(jsondata)
        #parser(e)
        #print(str(res.docs[element]).replace('Document ',''))
        #jsonvalues = json.dumps(str(res.docs[element]).replace('Document ','').replace('\'', '\"').replace('None', 'null'))
        
        #jsonObject[element]=json.dumps(str(res.docs[element]).replace('Document ','').replace('\'', '\"').replace('None', 'null'))
    #return json.dumps(res)
    #print(json.loads(jsonvalues))
    
    
    #return Response(json.loads(jsonObject), status=200, mimetype='application/json' )
    
    # Final JSON Array 
    #print(jsonArray)
    returnObject = { 'response' : jsonArray }
    print(returnObject)
    returnObject = json.dumps(returnObject)
    return Response(returnObject, status=200, mimetype='application/json' );

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
    app.run(host='0.0.0.0') # default = with debugger (will not show the custom Error pages)
    