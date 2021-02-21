
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
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW



#check if the new styleId already exists in database
def alreadyExists(new_skuId):
     if collection.find({'product_sku_id': new_skuId}).count() > 0:
         return True
     else:
         return False

#get the styleId from database
def get_styleId_fromDB():
    query = {'product_sku_id': {'$exists': 1}}
    projection = {'_id': 0, 'product_sku_id': 1}

    data = list(collection.find(query, projection))

    skuId_list = []
    for sku_id in data:
        skuId_list.append(sku_id['product_sku_id'])
    return skuId_list

class FlightClub:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://www.flightclub.com/catalogsearch/result?query={}'.format(stylId)
        driver = webdriver.Chrome('./chromedriver') 
        driver.set_window_position(-10000,0) 
        driver.get(url)  
        time.sleep(5) 
        html = driver.page_source 
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(html, "html.parser") 
        all_divs = soup.find('div', {'class' : 'sc-12ddmbl-0 kEGgBM'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            return href_url['href']
        else:
            return None   
        driver.close() # closing the webdriver 
        

    def get_fromFlight(self, url):
          page_url = "https://www.flightclub.com" + url
          response = requests.get(page_url)
          # Now, we could simply apply bs4 to html variable 
          soup = BeautifulSoup(response.content, "html.parser") 
          size_priceInfo = json.loads(soup.find('script', {'id' : '__NEXT_DATA__'}).text)
          if size_priceInfo is not None:
               json_object = size_priceInfo["props"]["pageProps"]['productTemplate']['newSizes']
               size_length = len(size_priceInfo["props"]["pageProps"]['productTemplate']['newSizes'])
               size_price =  []
               for index in range(size_length):
                    s = json_object[index]['size']['value']
                    p = json_object[index]['lowestPriceOption']['price']['display']
                    size_price.append([s, p])
               return size_price
          else: 
               return None

class scraperThread_forFlight(threading.Thread):
     def __init__(self, _styleId_list):
         threading.Thread.__init__(self)
         self._styleId_list = _styleId_list
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_flight(self._styleId_list)
         # Free lock to release next thread
         threadLock.release()


def thread_for_flight(list):
     for styleId in list:
          url = flight.search_ByStyleId(styleId)
          if url is not None:
               product_url = "https://www.flightclub.com" + url
               collection.update({'product_sku_id': styleId}, {'$set':{"product_flight_url":product_url}})
               print("success of adding the url from Flight Club")
               #size_priceInfo = flight.get_fromFlight(url)
               #if(size_priceInfo is not None):
               #     collection.update({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":size_priceInfo}})
               #     print("success of scraping from Flight Club")
                    
               #else:
               #     print("product not exist in Flight Club")
               #     collection.update({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":"-"}})
          else:
               continue

def scraper_function():
     
     styleId_list = get_styleId_fromDB()
     thread_flight = scraperThread_forFlight(styleId_list)
     thread_flight.start()
     thread_flight.join()

def update_function():
     styleId_list = get_updateList()
     thread_flight = scraperThread_forFlight(styleId_list)
     thread_flight.start()
     thread_flight.join()

def get_updateList():
     input_list = []
     print("ASICS","CONVERSE","JORDAN","NEW BALANCE","NIKE","OTHER","PUMA","REEBOK","SAUCONY","ARMOUR","VANS","YEEZY","ADIDAS")
     input_str = input('Input the brand name for scraping: ')
     input_list  = input_str.split(",")
     skuId_list = []
     upper_brand = ''
     for brand_name in input_list:
          if not brand_name.isupper():
               upper_brand = brand_name.upper()
          else:
               upper_brand = brand_name
          print(upper_brand)
          #get the styleId from database using brand name.
          cursor_list = collection.find({'product_brand': {'$regex':upper_brand}})
          print(cursor_list)
          for doc in cursor_list:
               skuId_list.append(doc['product_sku_id'])
     print(skuId_list)
     return skuId_list

if __name__ == "__main__":

     # flag for updating the scraped data.
     upadte_flag = True
     flight = FlightClub()
     threadLock = threading.Lock()
     try: 
          conn = MongoClient() 
          print("Connected successfully!!!") 
     except:   
          print("Could not connect to MongoDB") 
     sneaker_1 = Sneak()
     # database 
     db = conn.sneaks4sure 
     # Created or Switched to collection names: my_gfg_collection 
     collection = db.Sneakers
     #check if update or initial scrape
     if not upadte_flag:
          print("scrapping.....")
          scraper_function()
     else:
          print("updating....")
          update_function()
