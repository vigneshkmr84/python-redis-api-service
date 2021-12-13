# Redis Cache Service

### Run the app

Set the environment variables
``` bash 
export FLASK_ENV=development
export FLASK_APP=app.py
``` 

Run the app.py
``` bash
python3 -m flask run --port 5000
```

__Sample Input Data:__

``` json 
   { 
      "id": 1, 
      "first_name": "Elaine", 
      "last_name": "Dallosso", 
      "email": "edallosso0@networkadvertising.org",
      "product": "Soup Campbells Beef With Veg", 
      "address": "575 Portage Hill",
      "phone_number": "659-993-4818", 
      "count": 17, 
      "cost": 21.38, 
      "currency": "USD" 
   }

```

### Creating Index on Redis Parameters
``` FT.CREATE users on hash prefix 1 user: schema first_name text sortable last_name text sortable email  text sortable product text sortable phone_number text sortable ```


##### Sample Curl Input Data

``` bash 
curl -X POST -H 'Content-Type:application/json' http://localhost:5000/insert -d '{ "id": 1, "first_name": "Elaine", "last_name": "Dallosso", "email": "edallosso0@networkadvertising.org",   "product": "Soup Campbells Beef With Veg", "address": "575 Portage Hill",  "phone_number": "659-993-4818", "count": 17, "cost": 21.38, "currency": "USD" }'

curl -X POST -H 'Content-Type:application/json' http://localhost:5000/insert -d '{"id":2,"first_name":"Jacqueline","last_name":"Dodell","email":"jdodell1@ft.com","product":"Toamtoes 6x7 Select","address":"8973 Morning Hill","phone_number":"866-895-6921","count":6,"cost":12.83,"currency":"USD"}'

curl -X POST -H 'Content-Type:application/json' http://localhost:5000/insert -d '{"id":3,"first_name":"Olimpia","last_name":"Milne","email":"omilne2@liveinternet.ru","product":"Beans - Wax","address":"234 Ridge Oak Trail","phone_number":"800-110-2885","count":11,"cost":9.29,"currency":"USD"}'
```



