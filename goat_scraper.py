
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
from proxy import get_session, get_free_proxies, get_random_hdr, get_random_proxy

proxy = {
    'http':'http://andrea.pasinelli:FzX6tM3Q@92.249.19.239:35812',
    'https': 'https://andrea.pasinelli:FzX6tM3Q@92.249.19.239:35812'                   
    }

base_header = { 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': '__cfduid=d4c4c72c8d37b362c29c87137dcb793a41612681379',
    'if-none-match': 'W/"4ba45-ZegtekLtETaoF4PFHd6OYPcL2kE"',
    'sec-fetch-dest': 'document' ,
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
    }
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

class Goat:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://www.goat.com/search?query={}'.format(stylId)
        driver = webdriver.Chrome('./chromedriver') 
        driver.set_window_position(-10000,0) 
        driver.get(url)  
        time.sleep(5) 
        html = driver.page_source 
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(html, "html.parser") 
        all_divs = soup.find('div', {'class' : 'Grid__CellContent-sc-1njij7e-1 iZedTG'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            return href_url['href']
        else:
            return None   
        driver.close() # closing the webdriver 
        

    def get_fromGoat(self, url, base_header, proxy):
        page_url = "https://www.goat.com/web-api/v1/product_variants?productTemplateId=" + url
        # response = requests.get(page_url, headers=base_header, proxies = proxy, verify = False)
        i = 0
        while requests.exceptions.ConnectionError:
            try:
                proxy = get_random_proxy()
                resp = requests.get(page_url, headers=base_header, proxies = proxy, verify = False)
                break
            except requests.exceptions.ConnectionError as ex:
                i = i + 1
                print("connection error...{}--->".format(i), ex)
                
        while resp.status_code == 403 or resp.status_code == 502:
            print("get price-size data error 403")
            hdr = get_random_hdr()
            hhdr = hdr.strip();
            base_header["if-none-match"] = hhdr
            proxy = get_random_proxy()
            try:
                resp = requests.get(page_url, headers=base_header, proxies = proxy, verify = False)
            except Exception as ex:
                print("Exception in price-size", proxy)
                proxy = get_random_proxy()
        # Now, we could simply apply bs4 to html variable 
        if resp.status_code ==  200:
            soup = BeautifulSoup(resp.content, "html.parser")
            size_length = len(json.loads(soup.text))
            size_json = json.loads(soup.text)
            size_price =  []
            for index in range(size_length):
                s = size_json[index]['size']
                p = size_json[index]['lowestPriceCents']['amount']/100
                size_price.append([s, p])
            return size_price
        else:
            print(response.status_code) 
            return None

class scraperThread_forGoat(threading.Thread):
     def __init__(self, _styleId_list):
         threading.Thread.__init__(self)
         self._styleId_list = _styleId_list
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_goat(self._styleId_list)
         # Free lock to release next thread
         threadLock.release()


def thread_for_goat(list):
     for styleId in list:
            url = goat_1.search_ByStyleId(styleId)
            real_url  = url.split("/")
            if real_url[2] is not None:
                product_url = "https://www.goat.com/sneakers/" +  real_url[2]
                collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_url":product_url}})
                size_priceInfo = goat_1.get_fromGoat(real_url[2], base_header, proxy)
                if(size_priceInfo is not None):
                        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_priceSize":size_priceInfo}})
                        print("success of scraping from goat Club")
                        
            else:
               print("product not exist in Flight Club")
               collection.update({'product_sku_id': styleId}, {'$set':{"product_goat_priceSize":"-"}})




def scraper_function():
     
     styleId_list = get_styleId_fromDB()
     thread_flight = scraperThread_forGoat(styleId_list)
     thread_flight.start()
     thread_flight.join()


def update_function():
    styleId_list = get_updateList()
    # thread_for_goat(styleId_list)
    thread_flight = scraperThread_forGoat(styleId_list)
    thread_flight.start()
    thread_flight.join()

def get_updateList():
    input_list = []
    print("ASICS","CONVERSE","JORDAN","NEW BALANCE","NIKE","OTHER","PUMA","REEBOK","SAUCONY","UNDER ARMOUR","VANS","YEEZY","ADIDAS")
    input_str = input('Input the brand name for scraping: ')
    input_list  = input_str.split()
    skuId_list = []
    for brand_name in input_list:
        print(brand_name)
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
    
    goat_1 = Goat()
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
        print("scrapping.....")
        scraper_function()
    else:
        print("updating......")
        update_function()
    
