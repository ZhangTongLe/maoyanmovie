import requests
from requests import RequestException
from bs4 import BeautifulSoup as bs
import json
from multiprocessing import Pool

def get_one_page(url):
    try:

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        return response.text
    except RequestException:
        return None

def parse_one_page(html):
    soup = bs(html, 'lxml')
    movies = soup.select('#app div.main dl.board-wrapper dd')
    if movies:
        for movie in movies:
            score1 = movie.select('i.integer')[0]
            score2 = movie.select('i.fraction')[0]
            yield {
                'index': movie.select('i.board-index')[0].get_text(),
                'image': movie.select('img.board-img')[0].get('data-src'),
                'title': movie.select('p.name a')[0].get_text(),
                'actors': movie.select('p.star')[0].get_text().strip()[3:],
                'showtime': movie.select('p.releasetime')[0].get_text()[5:],
                'score': score1.get_text() + score2.get_text(),
            }
        #

def save_to_file(data):
    data = json.dumps(data, ensure_ascii=False)
    with open('maoyan.txt', 'a') as f:
        f.write(data + '\n')


def main(i):
    url = 'http://maoyan.com/board/4?offset={}'.format(str(i))
    print(url)
    html = get_one_page(url)
    datas = parse_one_page(html)
    for data in datas:
        save_to_file(data)
    # with open('maoyan.txt', 'r') as f:
    #     data = f.read()
    #     print(data)

if __name__ == '__main__':
    # for i in range(10):
    #     main(i*10)

    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])