from woocommerce import API
import requests
from pymongo import MongoClient
import json

wcapi = API(
    url="https://www.sneaks4sure.com",
    consumer_key="ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4",
    consumer_secret="cs_8eff2c58867228d9f2e326b9e236a690dbf3a962",
    wp_api=True,
    version="wc/v3"
)
category_index = {
    "ASICS": 58,
    "CONVERESE": 56,
    "JORDAN":47,
    "NEW BALANCE":60,
    "PUMA":48,
    "REEBOK":64,
    "SAUCONY":59,
    "UNDER ARMOUR":69,
    "VANS":57,
    "YEEZY":67,
    "ADIDAS":46,
    "NIKE":23
}

url = "https://www.sneaks4sure.com/wp-json/wc/v3/products?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'authorization': 'Basic YWRtaW46YWRtaW4yMDIwISE='}
image_url = "https://www.sneaks4sure.com/wp-json/wp/v2/media"
image_headers = {'Content-type': 'image/jpg', 'authorization': 'Basic YWRtaW46YWRtaW4yMDIwISE='}

def get_all_fieldsName():
    field_name = []
    cursor = collection.find_one({})
    for document in cursor: 
        field_name.append(document) 
    return field_name
def get_price_size_item():
    fields = []
    price_fields = []
    url_fields = []
    fields =  get_all_fieldsName()
    for s in fields:
        if 'price' in s: 
            price_fields.append(s)
        if 'url'  in s:
            if 'image_url' in s:
                continue
            url_fields.append(s)
    count = sum('price' in s for s in fields)
    return count, price_fields, url_fields

def get_imageId(image_arr = []):
    res = requests.post(image_url, data=json.dumps(image_arr), headers=image_headers)
    print (res.json())

def get_product_fromSKU(sku_id):
    cursor = collection.find({"product_sku_id": sku_id})
    for doc in cursor:
        p_name = doc['product_name']
        p_description = doc['product_description']
        p_sku = doc['product_sku_id']
        p_colorway = doc['product_colorway']
        p_releaseDate = doc['product_release_date']
        p_shortDescription = "<p>" + p_description + "</p><ul><li>SKU : " + p_sku + "</li><li>Release date :" + p_releaseDate + "</li><li>Colorway :" + p_colorway + "</li></ul>"
        p_regular_price = doc['product_last_sale']
        p_categories = doc['product_brand']
        p_categories_id = category_index[p_categories]
        p_image = doc['product_image_url']
        images_360view = p_image['360']
        image_big = p_image['imageUrl']
        image_thumb = p_image['thumbUrl']
        p_stock_price_size = []
        p_stock_price_size = doc['product_size_price']
        if 'product_withenew_priceSize' in doc:
            p_whenew_price_size = doc['product_withenew_priceSize']
        
            price_size_list = [p_stock_price_size, p_whenew_price_size]
        else:
            price_size_list = [p_stock_price_size]
        images_array = []
        meta_data_array = []
        length_meta = len(p_stock_price_size)
        # if product has 360views
        if len(images_360view) != 0:
            has360_views = True
            for index in range(len(images_360view)):
                image_per360 = {
                    # "id": 22505,
                    "src": images_360view[index],
                    "name": p_name + str(index) + ".jpg",
                    "alt":""
                }
                images_array.append(image_per360)
            # images_id = get_imageId(images_array)
            total_price_type = 1
            
            website_list = ["stockx"]
            for brand_type in range(total_price_type):
                size_price = []
                website_name = website_list[brand_type]
                size_price = price_size_list[brand_type]
                if size_price == '-':
                    continue
                for meta_index in range(length_meta):
                    per_meta = []
                    per_meta = [
                        {
                            "key": "sizes_" + str(meta_index) +"_currency",
                            "vlaue": "us"
                        },
                        {
                            "key": "_sizes_" + str(meta_index) +"_currency",
                            "value": "field_5f55e29250d3c"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand",
                            "value": ""
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand",
                            "value": "field_5f55e25d50d3b"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_size",
                            "value": size_price[meta_index][0]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_size",
                            "value": "field_5f55e20d50d38"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_price",
                            "value": size_price[meta_index][1]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_price",
                            "value": "field_5f55e23750d39"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand_name",
                            "value": website_name
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand_name",
                            "value": "field_5f55ef40aafa9"
                        }
                    ]
                    
                    meta_data_array.extend(per_meta)
            post_view = [
                {
                    "key": "sizes",
                    "value": str(length_meta)
                },
                {
                    "key": "_sizes",
                    "value": "field_5f55e1f250d37"
                },
                
                {
                    "key": "post_views_count",
                    "value": "316"
                },
                {
                    "key": "_post_views_count",
                    "value": ""
                }
            ]
            # magic_image = {
            #     "key": "_magic360_data",
            #     "value": "{\"images_ids\":image_array,\"options\":{\"checked\":false,\"columns\":5,\"set_columns\":false}}"
            # }
            # meta_data_array.append(magic_image)
            meta_data_array.extend(post_view)

        else:
            has360_views = False
            i_array = [image_big, image_thumb]
            for index in range(len(i_array)):
                image_perPro = {
                    # "id": 22505,
                    "src": i_array[index],
                    "name": p_name + str(index) + ".jpg",
                    "alt":""
                }
                images_array.append(image_perPro)
            # images_id = get_imageId(images_array)
            total_price_type = get_price_size_item()
            
            website_list = ["stockx","whenew", "flight club", "goat"]
            for brand_type in range(total_price_type):
                size_price = []
                website_name = website_list[brand_type]
                size_price = price_size_list[brand_type]
                if size_price == '-':
                    continue
                for meta_index in range(length_meta):
                    per_meta = []
                    per_meta = [
                        {
                            "key": "sizes_" + str(meta_index) +"_currency",
                            "vlaue": "us"
                        },
                        {
                            "key": "_sizes_" + str(meta_index) +"_currency",
                            "value": "field_5f55e29250d3c"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand",
                            "value": ""
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand",
                            "value": "field_5f55e25d50d3b"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_size",
                            "value": size_price[meta_index][0]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_size",
                            "value": "field_5f55e20d50d38"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_price",
                            "value": size_price[meta_index][1]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_price",
                            "value": "field_5f55e23750d39"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand_name",
                            "value": website_name
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand_name",
                            "value": "field_5f55ef40aafa9"
                        }
                    ]
                    meta_data_array.extend(per_meta)
            post_view = [
                {
                    "key": "sizes",
                    "value": "44"
                },
                {
                    "key": "_sizes",
                    "value": "field_5f55e1f250d37"
                },
                
                {
                    "key": "post_views_count",
                    "value": "316"
                },
                {
                    "key": "_post_views_count",
                    "value": ""
                }
            ]
            # meta_data_array.append(magic_image)
            meta_data_array.extend(post_view)
        data = {
            "name": p_name,
            "type": "simple",
            "status": "publish",
            "catalog_visibility": "visible",
            "description": p_description,
            "short_description": p_shortDescription,
            "sku": p_sku,
            "price": p_regular_price,
            "regular_price": p_regular_price,
            "stock_status": "instock",
            "categories": [
                {
                    "id": p_categories_id,
                    "name": p_categories,
                    "slug": p_categories
                }
            ],
            "images": images_array,
        "default_attributes": [],
        "variations": [],
        "grouped_products": [],
        "menu_order": 0,
        "meta_data": meta_data_array
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        if res.status_code == 201:
            if has360_views:
                json_data = json.loads(res.text)
                product_id = json_data['id']
                images_id = []
                id_str = ''
                for image in json_data['images']:
                    id = image['id']
                    images_id.append(id)
                    if id_str == '':
                        temp_str = str(id)     
                    else:
                        temp_str = id_str + "," + str(id) 
                    id_str = temp_str
                
                value_magic = "{\"images_ids\":["+ id_str + "], " + "\"options\":{\"checked\":false,\"columns\":5,\"set_columns\":false}}"
                data = {
                    "meta_data":[
                        {
                            "key": "_magic360_data",
                            "value": value_magic
                        }
                    ]
                }
                put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
                res = requests.put(put_url, data=json.dumps(data), headers=headers)
            else:
                continue
            # print (res.json())
            print(res.status_code)
        elif res.status_code == 400:
            print("product already exist..., so only update the price-size information")
            json_data = json.loads(res.text)
            product_id = json_data['data']['resource_id']
            data = {
                "meta_data":meta_data_array
            }
            put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
            res = requests.put(put_url, data=json.dumps(data), headers=headers)
            
def all_products_load():
    
    for product in collection.find({}, {"_id":0}):  
        p_name = product['product_name']
        p_description = product['product_description']
        p_sku = product['product_sku_id']
        p_colorway = product['product_colorway']
        p_releaseDate = product['product_release_date']
        p_shortDescription = "<p>" + p_description + "</p><ul><li>SKU : " + p_sku + "</li><li>Release date :" + p_releaseDate + "</li><li>Colorway :" + p_colorway + "</li></ul>"
        p_regular_price = product['product_last_sale']
        p_categories = product['product_brand']
        p_categories_id = category_index[p_categories]
        p_image = product['product_image_url']
        images_360view = p_image['360']
        image_big = p_image['imageUrl']
        image_thumb = p_image['thumbUrl']
        p_stock_price_size = []
        p_stock_price_size = product['product_size_price']
        p_whenew_price_size = product['product_withenew_priceSize']
        p_flight_price_size = product['product_flight_priceSize']
        p_flight_url = product['product_flight_url']
        p_stackx_url = product['product_stock_url']
        
        total_price_type, price_size_list, url_fields_list = get_price_size_item()
        images_array = []
        meta_data_array = []
        length_meta = len(p_stock_price_size)
        # if product has 360views
        if len(images_360view) != 0:
            has360_views = True
            for index in range(len(images_360view)):
                image_per360 = {
                    # "id": 22505,
                    "src": images_360view[index],
                    "name": p_name + str(index) + ".jpg",
                    "alt":""
                }
                images_array.append(image_per360)
            # images_id = get_imageId(images_array)
            website_list = ["stockx","withenew", "flight club", "goat"]
            for brand_type in range(total_price_type):
                size_price = []
                website_name = website_list[brand_type]
                size_price = price_size_list[brand_type]
                website_url = url_fields_list[brand_type]
                if size_price == '-':
                    continue
                for meta_index in range(length_meta):
                    per_meta = []
                    per_meta = [
                        {
                            "key": "sizes_" + str(meta_index) +"_currency",
                            "vlaue": "us"
                        },
                        {
                            "key": "_sizes_" + str(meta_index) +"_currency",
                            "value": "field_5f55e29250d3c"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand",
                            "value": ""
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand",
                            "value": "field_5f55e25d50d3b"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_size",
                            "value": size_price[meta_index][0]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_size",
                            "value": "field_5f55e20d50d38"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_price",
                            "value": size_price[meta_index][1]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_price",
                            "value": "field_5f55e23750d39"
                        },
                        {
                            "key": "sizes_"+ str(meta_index) +"_product_url",
                            "value": website_url
                        },
                        {
                            "key": "_sizes_"+ str(meta_index) +"_product_url",
                            "value": "field_5f55ef68aafaa"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand_name",
                            "value": website_name
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand_name",
                            "value": "field_5f55ef40aafa9"
                        }
                        
                    ]
                    
                    meta_data_array.extend(per_meta)
            post_view = [
                {
                    "key": "sizes",
                    "value": str(length_meta)
                },
                {
                    "key": "_sizes",
                    "value": "field_5f55e1f250d37"
                },
                
                {
                    "key": "post_views_count",
                    "value": "316"
                },
                {
                    "key": "_post_views_count",
                    "value": ""
                }
            ]
            # magic_image = {
            #     "key": "_magic360_data",
            #     "value": "{\"images_ids\":image_array,\"options\":{\"checked\":false,\"columns\":5,\"set_columns\":false}}"
            # }
            # meta_data_array.append(magic_image)
            meta_data_array.extend(post_view)

        else:
            has360_views = False
            i_array = [image_big, image_thumb]
            for index in range(len(i_array)):
                image_perPro = {
                    # "id": 22505,
                    "src": i_array[index],
                    "name": p_name + str(index) + ".jpg",
                    "alt":""
                }
                images_array.append(image_perPro)
            # images_id = get_imageId(images_array)
            total_price_type, price_size_list, url_fields_list = get_price_size_item()
            
            website_list = ["stockx","whenew", "flight club", "goat"]
            for brand_type in range(total_price_type):
                size_price = []
                website_name = website_list[brand_type]
                size_price = price_size_list[brand_type]
                website_url = url_fields_list[brand_type]
                if size_price == '-':
                    continue
                for meta_index in range(length_meta):
                    per_meta = []
                    per_meta = [
                        {
                            "key": "sizes_" + str(meta_index) +"_currency",
                            "vlaue": "us"
                        },
                        {
                            "key": "_sizes_" + str(meta_index) +"_currency",
                            "value": "field_5f55e29250d3c"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand",
                            "value": ""
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand",
                            "value": "field_5f55e25d50d3b"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_size",
                            "value": size_price[meta_index][0]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_size",
                            "value": "field_5f55e20d50d38"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_price",
                            "value": size_price[meta_index][1]
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_price",
                            "value": "field_5f55e23750d39"
                        },
                        {
                            "key": "sizes_"+ str(meta_index) +"_product_url",
                            "value": website_url
                        },
                        {
                            "key": "_sizes_"+ str(meta_index) +"_product_url",
                            "value": "field_5f55ef68aafaa"
                        },
                        {
                            "key": "sizes_" + str(meta_index) + "_brand_name",
                            "value": website_name
                        },
                        {
                            "key": "_sizes_" + str(meta_index) + "_brand_name",
                            "value": "field_5f55ef40aafa9"
                        }
                    ]
                    meta_data_array.extend(per_meta)
            post_view = [
                {
                    "key": "sizes",
                    "value": str(length_meta)
                },
                {
                    "key": "_sizes",
                    "value": "field_5f55e1f250d37"
                },
                
                {
                    "key": "post_views_count",
                    "value": "316"
                },
                {
                    "key": "_post_views_count",
                    "value": ""
                }
            ]
            # meta_data_array.append(magic_image)
            meta_data_array.extend(post_view)
        data = {
            "name": p_name,
            "type": "simple",
            "status": "publish",
            "catalog_visibility": "visible",
            "description": p_description,
            "short_description": p_shortDescription,
            "sku": p_sku,
            "price": p_regular_price,
            "regular_price": p_regular_price,
            "stock_status": "instock",
            "categories": [
                {
                    "id": p_categories_id,
                    "name": p_categories,
                    "slug": p_categories
                }
            ],
            "images": images_array,
        "default_attributes": [],
        "variations": [],
        "grouped_products": [],
        "menu_order": 0,
        "meta_data": meta_data_array
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        if res.status_code == 201:
            if has360_views:
                json_data = json.loads(res.text)
                product_id = json_data['id']
                images_id = []
                id_str = ''
                for image in json_data['images']:
                    id = image['id']
                    images_id.append(id)
                    if id_str == '':
                        temp_str = str(id)     
                    else:
                        temp_str = id_str + "," + str(id) 
                    id_str = temp_str
                
                value_magic = "{\"images_ids\":["+ id_str + "], " + "\"options\":{\"checked\":false,\"columns\":5,\"set_columns\":false}}"
                data = {
                    "meta_data":[
                        {
                            "key": "_magic360_data",
                            "value": value_magic
                        }
                    ]
                }
                put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
                res = requests.put(put_url, data=json.dumps(data), headers=headers)
            else:
                continue
            # print (res.json())
            print(res.status_code)
        elif res.status_code == 400:
            print("product already exist..., so only update the price-size information")
            json_data = json.loads(res.text)
            product_id = json_data['data']['resource_id']
            data = {
                "meta_data":meta_data_array
            }
            put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
            res = requests.put(put_url, data=json.dumps(data), headers=headers)


if __name__ == "__main__":
    
    # flag for updating the scraped data.
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    # Created or Switched to collection names
    collection = db.Sneakers
    
    all_products_load()