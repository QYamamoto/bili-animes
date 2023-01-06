import requests

from threading import Thread
import json

from models import Zero, Review, Anime, session

URL_ANIMES = 'https://api.bilibili.com/pgc/season/index/result?st=1&order=3&season_version=-1&spoken_language_type=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&sort=0&season_type=1&pagesize=20&type=1&page={}'
URL_CHINESE = 'https://api.bilibili.com/pgc/season/index/result?season_version=-1&is_finish=-1&copyright=-1&season_status=-1&year=-1&style_id=-1&order=3&st=4&sort=0&page={}&season_type=4&pagesize=20&type=1'
URL_ANIME = 'https://api.bilibili.com/pgc/review/{}/list?media_id={}&ps=20&sort=0&cursor={}'

def get(url, *params):
    try:
        res = json.loads(requests.get(url.format(*params)).text)
        if res['code'] != 0:
            raise Exception(res['message'])
        return res['data']
    except:
        raise

def get_animes():
    for url in (URL_ANIMES, URL_CHINESE):
        index = 1
        tasks = []
        while True:
            res = get(url, index)
            tasks.append(Thread(target=get_page, args=(res['list'], url == URL_CHINESE)))
            tasks[-1].start()
            print(index * 20, '/', res['total'])
            if not res['has_next']:
                break
            index += 1
        for task in tasks:
            task.join()
    session.commit()

def get_page(page, chinese):
    tasks = []
    for anime in page:
        tasks.append(Thread(target=get_anime, args=(anime['title'], Anime(
            media_id=anime['media_id'],
            chinese=int(chinese),
            title=anime['title']
        ))))
        tasks[-1].start()
    for task in tasks:
        task.join()

def get_anime(title, anime):
    global result
    print('正在获取:', title)
    for type in ('short', 'long'):
        review = Review(
            media_id=anime.media_id,
            type=(type == 'long')
        )
        cursor = 0
        index = 1
        while True:
            res = get(URL_ANIME, type, anime.media_id, cursor)
            for r in res['list']:
                if r['score'] == 0:
                    session.add(Zero(
                        media_id=anime.media_id,
                        name=r['author']['uname'],
                        uid=r['author']['mid'],
                        content=r['content']
                    ))
                review.add(r['score'])
            if 20 * index >= res['total']:
                break
            index += 1
            cursor = res['next']
        session.add(review)
    session.add(anime)
    print('获取完成:', title)

get_animes()