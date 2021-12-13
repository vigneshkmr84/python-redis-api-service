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





