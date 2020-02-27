import json
import time
import urllib.request
from urllib.request import urlopen

from kafka import KafkaProducer



API_KEY = "28c78dcf9e3577bf4eed4373701c9c7e54ef83fd"

url = "https://api.jcdecaux.com/vls/v1/stations?apiKey={}".format(API_KEY)

producer =  KafkaProducer(bootstrap_servers="localhost:9092")

velos_disponible = {}

while True:
    response = urlopen(url)
    stations = json.loads(response.read().decode('utf-8'))
    for station in stations:
        curr_available = station['available_bikes'] # current available bikes
        key = '{} - {}- {}'.format(station['number'], station['name'], station['contract_name'])
        
        if key not in velos_disponible:
            velos_disponible[key] = curr_available
        if (curr_available == 0 and velos_disponible[key]>0) or (curr_available >0  and velos_disponible[key]==0):
            # payload
            pload = {'key': key,
                    'name': station['name'],
                    'address': station['address'],
                    'available_bikes': curr_available,
                    'city': station['contract_name']}
            producer.send("empty-stations", json.dumps(pload).encode(),
                         key=str(key).encode())
            print('Name =({}) Address =({}) City =({}) Before={} Now={}'.format(station['name'], station['address'],
                                                                                station['contract_name'], velos_disponible[key],
                                                                                curr_available))
    
            print()
    time.sleep(1)