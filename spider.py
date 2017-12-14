import re
import pymongo
import requests
from requests.exceptions import RequestException
from config import *
from multiprocessing import Pool

client = pymongo.MongoClient(IP, PORT, connect=False)
db = client[DATABASE]
table = db['movie']

def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'
            ''
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?">(.*?)</i>.*?data-src="(.*?)".*?class="name"><a.*?">(.*?)</a>.*?"star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actors': item[3].strip()[3:],
            'showtime': item[4][5:],
            'score': item[5]+item[6]
        }

def save_to_mongo(item):
    try:
        table.update(item, {'$set': {'title': item['title']}}, upsert=True)
        print('save to mongo sucess\n', item)
    except Exception as e:
        print('failed to connect to mongo', e)



def main(offset):
    url = 'http://maoyan.com/board/4?offset={0}'.format(str(offset))
    html = get_one_page(url)
    # print(html)
    for data in parse_one_page(html):
        save_to_mongo(data)



if __name__ == '__main__':
    # for i in range(10):
    #     main(i*10)

    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])

