
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

#get the styleId from database
def get_styleId_fromDB():
    query = {'product_sku_id': {'$exists': 1}}
    projection = {'_id': 0, 'product_sku_id': 1}

    data = list(collection.find(query, projection))

    skuId_list = []
    for sku_id in data:
        skuId_list.append(sku_id['product_sku_id'])
    return skuId_list

class Withenew:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://wethenew.com/search?type=product&q={}*'.format(stylId)
        driver = webdriver.Chrome('./chromedriver')  
        driver.get(url)  
        time.sleep(5) 
        html = driver.page_source 
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(html, "html.parser") 
        all_divs = soup.find('a', {'class' : 'product-info__caption'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            return href_url['href']
        else:
            return None   
        driver.close() # closing the webdriver 
        

    def get_fromWithenew(self, url):
        page_url = "https://wethenew.com" + url
        response = requests.get(page_url)
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(response.content, "html.parser") 
        all_divs = soup.find('div', {'class' : 'selector-wrapper'})
        price_size = []
        if all_divs is not None: 
            option_list = all_divs.find('option')
            for each in option_list:
                str = each.text.split('-')
                price_size.append(str[1], str[0], str[2])
            return price_size
        else:
            return None

class scraperThread_forWithenew(threading.Thread):
     def __init__(self, _styleId_list):
        threading.Thread.__init__(self)
        self._styleId_list = _styleId_list
     def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        thread_for_withenew(self._styleId_list)
        # Free lock to release next thread
        threadLock.release()


def thread_for_withenew(list):
     for styleId in list:
            url = withenew_1.search_ByStyleId(styleId)
            if url is not None:
                size_priceInfo = withenew_1.get_fromWithenew(url)
                if(size_priceInfo is not None):
                        collection.update({'product_sku_id': styleId}, {'$set':{"product_withenew_priceSize":size_priceInfo}})
                        print("success of scraping from Withenew Club")
                        
            else:
               print("product not exist in Withenew Club")
               collection.update({'product_sku_id': styleId}, {'$set':{"product_withenew_priceSize":"-"}})




def scraper_function():
     
    styleId_list = get_styleId_fromDB()
    thread_for_withenew(styleId_list)
    #thread_flight = scraperThread_forWithenew(styleId_list)
    #thread_flight.start()
    #thread_flight.join()

def update_function():
    styleId_list = get_updateList()
    thread_flight = scraperThread_forWithenew(styleId_list)
    thread_flight.start()
    thread_flight.join()

def get_updateList():
    input_list = []
    input_str = input('Input the brand name for scraping: ')
    input_list  = input_str.split()
    skuId_list = []
    for brand_name in input_list:
        if not brand_name.isupper():
            upper_brand = brand_name.upper()
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
    withenew_1 = Withenew()
    threadLock = threading.Lock()
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
    if not upadte_flag:
        print("scrapping....")
        scraper_function()
    else:
        print("updating.....")
        update_function()
