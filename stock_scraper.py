from stockx import StockXAPI
from datetime import date
from pymongo import MongoClient
import threading
from sneaks_model import Sneak
# pprint library is used to make the output look more pretty
from pprint import pprint

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

proxy = {
    'http':'http://andrea.pasinelli:FzX6tM3Q@92.249.19.239:35812',
    'https': 'https://andrea.pasinelli:FzX6tM3Q@92.249.19.239:35812'                   
}



stockx = StockXAPI()
threadLock = threading.Lock()

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

class scraperThread (threading.Thread):
     def __init__(self, brand_name, page_number, upadte_flag):
        threading.Thread.__init__(self)
        self.brand_name = brand_name
        self.page_number = page_number
        self.upadte_flag = upadte_flag
     def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        if not upadte_flag:
            thread_for_eachPage(self.brand_name, self.page_number)
        else:
            thread_for_update(self.brand_name, self.page_number)
        # Free lock to release next thread
        threadLock.release()




def thread_for_eachPage(brand_name, page_number):

     products = stockx.search_items(search_term=brand_name, output_data=['id', 'urlKey', 'styleId'], page=page_number, max_searches=50)
     # Get the name, last sale price, and lowest ask from this id.
     for product_id in products:
         item_info, price_info = stockx.get_item_data(item_id=product_id['id'], output_data=['shoe','productCategory', 'retailPrice', 'releaseDate', 'media', 'shortDescription', 'description','styleId',
                                                                     'colorway',['market', 'lastSale'],['media', '360'],['media', 'imageUrl'],['media', 'smallImageUrl'],['media', 'thumbUrl'],
                                                                 ['market', 'changeValue'], ['market', 'changePercentage']])
       
         price_info = stockx.get_price_size(url_key=product_id['urlKey'], output_data = [])
         #check if the new sku_id
         if 'styleId' in item_info:
             if( (not (alreadyExists(item_info['styleId']))) and (item_info['styleId'] != '')):
                 # set the field parameter value for mongodb                                                            
                 if 'productCategory' in item_info:
                     sneaker_1.product_category = item_info["productCategory"]
                 else:
                     sneaker_1.product_category = ''
                 if 'shoe' in item_info:
                         sneaker_1.product_name = item_info["shoe"]
                 else:
                     sneaker_1.product_name = ''
                 if 'lastSale' in item_info:
                         sneaker_1.product_last_sale  = str(item_info['lastSale'])
                 else:
                     sneaker_1.product_last_sale = ''
                 if 'changeValue' in item_info:
                         sneaker_1.product_change_value = str(item_info['changeValue'])
                 else:
                     sneaker_1.product_change_value = ''
                 if 'changePercentage' in item_info:
                         sneaker_1.product_change_percentage = str(item_info['changePercentage'])
                 else:
                     sneaker_1.product_change_percentage = ''
                 if 'media' in item_info:
                         sneaker_1.product_image_url = item_info['media']
                        
                 else:
                     sneaker_1.product_image_url = ''
               
                 if 'styleId' in item_info:
                         sneaker_1.product_style_id = item_info['styleId']
                         sneaker_1.product_sku_id = item_info['styleId']
                
                 if 'colorway' in item_info:
                         sneaker_1.product_colorway = item_info["colorway"]
                 else:
                     sneaker_1.product_colorway = ''
                
                 if 'retailPrice' in item_info:
                         sneaker_1.product_retail_price = str(item_info['retailPrice'])
                 else:
                     sneaker_1.product_retail_price = ''
                
                 if 'releaseDate' in item_info:
                         sneaker_1.product_release_date = str(item_info['releaseDate'])
                 else:
                     sneaker_1.product_release_date = ''
                
                 if 'description' in item_info:
                         sneaker_1.product_description = item_info["description"]
                 else:
                     sneaker_1.product_description = ''
                
                 sneaker_1.product_size_price = price_info
                
                 collection.insert_one(sneaker_1.to_dict())      



def thread_for_update(brand_name, page_number):
    products = stockx.search_items(search_term=brand_name, output_data=['id', 'urlKey', 'styleId'], proxy = proxy, page=page_number, max_searches=50)
    # Get the name, last sale price, and lowest ask from this id.
    for product_id in products:
        #Get the price-size info of each product.
        price_info = stockx.get_price_size(url_key=product_id['urlKey'], output_data = [])
        #find the same id from database
        collection.find_one_and_update({"product_sku_id" : product_id['styleId']},{"$set":{"product_size_price": price_info}},upsert=True)
        print("success of updating price size information.....")



def scraper_function():
    print("---------------------------------------------------------------------------")
    print("scrapping......")

    #---------------this is step code for initial scrapping.----------------- 
    for brand in brand_list:
        # iterate all of the 25 pages
        for page in range(25):
            each_thread = scraperThread(brand, page, False)
            each_thread.start()
            each_thread.join()

    print("finished the scrapping.....")
    print("---------------------------------------------------------------------------")

def update_fuction():
    input_list = []
    input_str = input('Input the brand name for scraping: ')
    input_list  = input_str.split()
    skuId_list = []
    for brand_name in input_list:
        if not brand_name.isupper():
            upper_brand = brand_name.upper()
            print(upper_brand)
        for page in range(25):
            each_thread = scraperThread(upper_brand, page, True)
            each_thread.start()
            each_thread.join()

if __name__ == "__main__":

    # flag for updating the scraped data.
    upadte_flag = True
    if not upadte_flag:
        brand_list = stockx.get_brands(output_data = [])
        print(brand_list)
        scraper_function()
    else:
        print("updating...")
        update_fuction()

