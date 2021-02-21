from datetime import date
from pymongo import MongoClient
import threading
import lxml
import lxml.html
from bs4 import BeautifulSoup
import requests
import json
import time
from selenium import webdriver 
from sneaks_model import Sneak
from pprint import pprint


def read_fields_fromJson():
    with open('Sneakers_Flight.json') as f:
        data = json.load(f)
    return data

def get_styleId_fromDB():
    query = {'product_sku_id': {'$exists': 1}}
    projection = {'_id': 0, 'product_sku_id': 1}

    data = list(collection.find(query, projection))

    skuId_list = []
    for sku_id in data:
        skuId_list.append(sku_id['product_sku_id'])
    return skuId_list

def insert_newField_inDB():
    json_data  = read_fields_fromJson()
    skuId_list = get_styleId_fromDB()
    
    for each_json in json_data:
        if 'product_flight_priceSize' in each_json and 'product_flight_url' in each_json:
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_priceSize":each_json['product_flight_priceSize']}})
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_url":each_json['product_flight_url']}})
        elif 'product_flight_priceSize' not in each_json and 'product_flight_url' in each_json:
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_priceSize":'-'}})
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_url":each_json['product_flight_url']}})
        elif 'product_flight_url' not in each_json and 'product_flight_priceSize' in each_json:
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_priceSize":each_json['product_flight_priceSize']}})
            collection.update_one({'product_sku_id': each_json['product_sku_id']}, {'$set':{"product_flight_url":''}})
            
    print("updated....")
if __name__ == "__main__":
    
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    sneaker_1 = Sneak()
    # database 
    db = conn.sneaks4sure 
    # Created or Switched to collection names
    collection = db.Sneakers    
    insert_newField_inDB()