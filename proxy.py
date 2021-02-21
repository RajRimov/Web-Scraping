
import requests
import random
from bs4 import BeautifulSoup as bs
import numpy as np

proxies = []
def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = bs(requests.get(url).content, "html.parser")
  
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies
def get_session(proxies):
    # construct an HTTP session
    session = requests.Session()
    # choose one random proxy
    proxy = random.choice(proxies)
    session.proxies = {"http": proxy, "https": proxy}
    return session

def get_random_hdr():
    random_hdr = ''
    header_file = 'header.txt'
    try:
        with open(header_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_hdr = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_hdr

def get_random_proxy():
    random_proxy = ''
    proxy_instance = {
        'http': "http://10.10.1.10:3128",
        'https': "https://10.10.1.11:1080"
    }
    proxy_file = 'proxy.txt'
    try:
        with open(proxy_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            selected_proxy = lines[int(idx)]
            random_proxy = selected_proxy.strip()
            proxy = random_proxy.split(':')
            http_proxy = "http://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + ":" + proxy[1] 
            https_proxy = "https://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + ":" + proxy[1]
            proxy_instance['http'] = http_proxy
            proxy_instance['https'] = https_proxy
              
    except Exception as ex:
        print('Exception in random_proxy')
        print(str(ex))
    finally:
        return proxy_instance


proxies = get_random_proxy()
