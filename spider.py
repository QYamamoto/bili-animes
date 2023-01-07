import requests

from threading import Thread, Lock
import json

from models import Zero, Review, Anime, get_session

URL_ANIMES = 'https://api.bilibili.com/pgc/season/index/result?st=1&order=3&season_version=-1&spoken_language_type=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&sort=0&season_type=1&pagesize=20&type=1&page={}'
URL_CHINESE = 'https://api.bilibili.com/pgc/season/index/result?season_version=-1&is_finish=-1&copyright=-1&season_status=-1&year=-1&style_id=-1&order=3&st=4&sort=0&page={}&season_type=4&pagesize=20&type=1'
URL_ANIME = 'https://api.bilibili.com/pgc/review/{}/list?media_id={}&ps=20&sort=0&cursor={}'

lock = Lock()
count = 1

def get(url, *params):
    url = url.format(*params)
    try:
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f'''url: {url}
状态码: {res.status_code}
响应: {res.text}''')
        content = res.text
        res = json.loads(content)
        if res['code'] != 0:
            raise Exception(url + ' ' + res['message'])
        return res['data']
    except Exception as ex:
        raise Exception(f'''url: {url}
响应: {content}
原因: {ex}''')

def get_animes():
    tasks = []
    for url in (URL_ANIMES, URL_CHINESE):
        index = 1
        while True:
            res = get(url, index)
            tasks.append(Thread(target=get_page, args=(res['list'], url == URL_CHINESE)))
            tasks[-1].start()
            print(f'{index * 20} / {res["total"]}')
            if not res['has_next']:
                break
            index += 1
    for task in tasks:
        task.join()

def get_page(page, chinese):
    tasks = []
    for anime in page:
        tasks.append(Thread(target=get_anime, args=(Anime(
            media_id=anime['media_id'],
            chinese=chinese,
            title=anime['title'],
            score=anime['score']
        ), )))
        tasks[-1].start()
    for task in tasks:
        task.join()

def get_anime(anime):
    global count
    session = get_session()
    print(f'正在获取: {anime.title} {anime.media_id}')
    if session.query(Anime).get(anime.media_id):
        with lock:
            count += 1
            print(f'获取完成: {anime.title} {anime.media_id} 第{count}个')
        return
    for type in ('short', 'long'):
        review = Review(
            media_id=anime.media_id,
            type=(type == 'long'),
        )
        cursor = 0
        index = 1
        while True:
            while True:
                try:
                    res = get(URL_ANIME, type, anime.media_id, cursor)
                    break
                except Exception:
                    pass
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
    with lock:
        session.add(anime)
        session.commit()
        count += 1
        print(f'获取完成: {anime.title} {anime.media_id} 第{count}个')

get_animes()