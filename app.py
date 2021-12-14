
from flask import Flask, request
from datetime import datetime
from flask.wrappers import Response
from types import SimpleNamespace
from collections import namedtuple

from redisearch import Client, TextField, NumericField, Query

import json, redis


NOT_AVAILABLE = 'API Not found'
SERVER_ERROR = 'Internal Server Error'
INVALID_ARGUMENTS = 'Invalid Arguments Passed'

### KEY PREFIX
USER_KEY_PREFIX = 'user:'
TOTAL_KEYS = 'total'
SEARCH_INDEX = 'users'
SUCCESS_PREFIX='success:'
FAILURE_PREFIX='error:'

# Establishing Redis Connection (utf-8 is important else there will be a 'b' character representing it's a byte type)
connection = redis.Redis(host='localhost'
                         , charset='utf=8'
                         , decode_responses=True
                         , port=6379
                         , db=0)


app = Flask(__name__)

## This API is only for the first service to upsert the data
@app.route('/insert', methods=['POST'])
def insert():
    rawRequst = request.json
    id = rawRequst['id']
    status=""
    service_name=""
    try:
        status = request.args.get('status')
        service_name = request.args.get('serviceName')
    
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

## Updating the Status
@app.route('/status', methods=['POST'])
def statusUpdate():
    try:
        #status=request.args.get('status')
        #service_name=request.args.get('service')
        #error=request.args.get('error')
        rawRequst = request.json
        
        status=rawRequst['status']
        id=rawRequst['id']
        service_name=rawRequst['service']
        error=rawRequst['error']
        updateStatus(status, id, service_name, error)
        return Response('Updated Successfully', status=200, mimetype='application/json')     
    except ValueError:
        print('Exception occurred during status update')
        return Response(SERVER_ERROR, status=500, mimetype='application/json')
    

def updateStatus(status, id, service_name, error):
    
    if status == 'success':
        key= SUCCESS_PREFIX + service_name
        connection.sadd(key, id)
    else:
        key=FAILURE_PREFIX + service_name
        print('Updating Failure records for key : ' + key)
        connection.sadd(key, id)
        key=key +':' + str(id)
        print('Recording Error message for key : ' + key)
        connection.set(key, error)
        
    
# API will find the set of total users in the list, and will iterate through them to fetch the data for each one.
@app.route('/get/all', methods=['GET'])
def getAll():
    print('Inside Get all Function', datetime.today())
    jsonArray = []
    try:
        #map=connection.hgetall('user:*')
        userSet = connection.smembers(TOTAL_KEYS)
        for key in connection.scan_iter("user:*", 5):
            # print the key
            element = connection.hgetall(key)
            #print(element)
            jsonArray.append(element)
        
        print('Total result - ' + str(len(jsonArray)))
        #returnObject = {'response': list(userSet)}
        returnObject = {'response': jsonArray}
        return Response(json.dumps(returnObject), status=200, mimetype='application/json')
    except redis.RedisError:
        print('Exception occurred during retrieval')
        return Response(SERVER_ERROR, status=500, mimetype='application/json')


    
@app.route('/search', methods=['GET'])
def search():
    query=request.args.get('query')
    print("Query = ", query)
    client = Client(SEARCH_INDEX)
    res = client.search(query)
    print('Total elements in result = ', res.total)
    jsonArray = []
    
    for element in range(res.total):
        e = res.docs[element]       
        jsonArray.append(parser(e))
        
    # Final JSON Array print(jsonArray)
    returnObject = { 'response' : jsonArray }
    
    return Response(json.dumps(returnObject), status=200, mimetype='application/json' );

## Function to parse the redis document from search to json object
def parser(doc):
    document_string = str(doc)
    json_string = document_string.replace('Document', '').replace('\'', '\"').replace('None', 'null')
    jsondata = json.loads(json_string)

    #print(jsondata)
    return jsondata;
    
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
    