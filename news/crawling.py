import requests
import os
from django.core.files import File
from io import BytesIO

from PIL import Image
import datetime
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from django.conf import settings

from news.models import NewsData

media_file = os.path.join(settings.BASE_DIR, 'media', 'news_image')


# 중앙일보
def news_joins():
    result = []
    url = 'https://news.joins.com/culture/song/list/1'
    # 해당 url get 요청후 response 저장
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")
    articles = html.select('.list_basic >.type_b.clearfx > li')
    # image file 구분
    n = 1
    for ar in articles:
        # title
        title = ar.select_one(".headline.mg > a").text

        # DB에 있는 title 비교 후 똑같은 title pass
        if not NewsData.objects.filter(title=title):
            # link
            link = "http://news.joins.com" + ar.find("a")["href"]
            # 현재시간
            now_date = datetime.datetime.now()
            if ar.find("img"):
                # img_src
                img_src = ar.select_one("img")['src']
                # 파일경로 저장
                file = media_file+"/joins" + now_date.strftime("%Y-%m-%d-%H-%M") + str(n) + '.jpg'
                # image 파일 저장
                urlretrieve(img_src, file)
            else:
                file = None
            date_list = ar.select('.byline > em')
            for li in date_list:
                date = li.text
                date = date.replace(".","-")

            crawling_obj = {
                'title': title,
                'link': link,
                'image': file,
                'date': date,
            }

            n += 1

            result.append(crawling_obj)
    return result


# 동아일보
def news_donga():
    result = []
    url = 'https://www.donga.com/news/Entertainment/List'
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")
    articles = html.select('.articleList')
    n = 1
    for ar in articles:
        title = ar.select_one(".tit").text
        if not NewsData.objects.filter(title=title):
            link = ar.find("a")["href"]
            date = ar.select_one(".date").text

            if ar.find("img") is not None:
                img_src = ar.find("img")["src"]
                # 현재시간
                now_date = datetime.datetime.now()
                # 파일경로 저장
                file = media_file + "/donga" + now_date.strftime("%Y-%m-%d-%H-%M") + str(n) + '.jpg'
                # image 파일 저장
                urlretrieve(img_src, file)
            else:
                file = None

            crawling_obj = {
                'title': title,
                'link': link,
                'image': file,
                'date': date,
            }

            n += 1

            result.append(crawling_obj)

    return result


# 연합뉴스
def news_yna():
    result = []
    url = "https://www.yna.co.kr/entertainment/pop-song/1"
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")
    articles = html.select('.box-type.box-latest01 >.list-type038 > .list > li')
    n = 1
    for ar in articles:
        if ar.select_one(".tit-news") is not None:
            title = ar.select_one(".tit-news").text

            if not NewsData.objects.filter(title=title):
                # 현재시간
                now_date = datetime.datetime.now()

                link = ar.find("a")["href"]
                link = "https:" + link

                img_src = ar.find("img")["src"]
                img_src = "https:" + img_src
                date = ar.select_one(".txt-time").text
                year = now_date.strftime("%Y") + "-"

                date = year + date
                if img_src:
                    # 파일경로 저장
                    file = media_file + "/yna" + now_date.strftime("%Y-%m-%d-%H-%M") + str(n) + '.jpg'
                    # image 파일 저장
                    urlretrieve(img_src, file)
                else:
                    file = None

                crawling_obj = {
                    'title': title,
                    'link': link,
                    'image': file,
                    'date': date,
                }

                n += 1

                result.append(crawling_obj)

    return result


# db 저장
def save():
    if os.path.exists(media_file):
        pass
    else:
        os.makedirs(media_file)
    print("start")
    # 중알일보 크롤링 결과 저장
    joins = news_joins()

    if joins is not None:
        for item in joins:
            if item is not None:
                try:
                    local_news_image = Image.open(item['image'])
                    output = BytesIO()
                    local_news_image.save(output, format=local_news_image.format, quality=102)
                    output.seek(0)
                    a = NewsData()
                    a.title = item['title']
                    a.link = item['link']
                    a.image = File(output, item['image'].split('/')[-1])
                    a.date = item['date']
                    a.save()
                    local_news_image.close()
                except Exception as ex:
                    NewsData(title=item['title'], link=item['link'], image=None, date=item['date']).save()
                    print("error", ex)

    # 동아일보 크롤링 결과 저장
    donga = news_donga()

    if donga is not None:
        for item in donga:
            if item is not None:
                try:
                    local_news_image = Image.open(item['image'])
                    output = BytesIO()
                    local_news_image.save(output, format=local_news_image.format, quality=100)
                    output.seek(0)
                    a = NewsData()
                    a.title = item['title']
                    a.link = item['link']
                    a.image = File(output, item['image'].split('/')[-1])
                    a.date = item['date']
                    a.save()
                    local_news_image.close()
                except:
                    print("error")
                    NewsData(title=item['title'], link=item['link'], image=None, date=item['date']).save()

    # 연합뉴스 크롤링 결과 저장
    yna = news_yna()

    if yna is not None:
        for item in yna:
            if item is not None:
                try:
                    local_news_image = Image.open(item['image'])
                    output = BytesIO()
                    local_news_image.save(output, format=local_news_image.format, quality=100)
                    output.seek(0)
                    a = NewsData()
                    a.title = item['title']
                    a.link = item['link']
                    a.image = File(output, item['image'].split('/')[-1])
                    a.date = item['date']
                    a.save()
                    local_news_image.close()
                except:
                    NewsData(title=item['title'], link=item['link'], image=None, date=item['date']).save()


def delete():
    NewsData.objects.all().delete()


if __name__ == '__main__':
    save()
