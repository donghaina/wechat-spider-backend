from app.models import Feed
from app.models import FeedSchema
from app.models import Post
from app.models import PostSchema
from app import db
import requests
import random
import wechatsogou
import os
import time
import pymysql
from lxml.html.clean import Cleaner
import jieba
from jieba import analyse
from bs4 import BeautifulSoup
import re
import random
ws_api = wechatsogou.WechatSogouAPI()


# 获取网页
def get_html(url):
    headers = {'user-agent': 'Mozilla/5.0'}
    response = requests.get(url=url, headers=headers, timeout=5)
    return response.content


# 获取HTML正文
def get_post_content(html_page):
    cleanr = re.compile('<.*?>')
    soup = BeautifulSoup(html_page, 'lxml')
    post_content = str(soup.find('div', class_="rich_media_content"))
    post_content_text = re.sub(cleanr, '', post_content)
    return post_content, post_content_text


# 提取文章关键词
def get_post_keywords(text):
    textrank = analyse.textrank
    keyword_list = textrank(text, topK=10)
    return ','.join(keyword_list)


# 获取所有的公众号昨天的数据
def get_all_feed_post_list():
    feed_list = Feed.query.order_by(Feed.scraping_time).all()
    feed_schema = FeedSchema(many=True)
    target_feed_list = feed_schema.dump(feed_list)
    update_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60))
    get_today_all_data(target_feed_list, update_date)


# 获取今日所有公众号更新的文章
def get_today_all_data(target_feed_list, update_date):
    start_time = time.time()
    yesterday = update_date
    for item in target_feed_list:
        wechat_title = item if (isinstance(item, str)) else item['wx_title']
        history_info = ws_api.get_gzh_article_by_history(wechat_title)
        history_articles = history_info['article']
        for article in history_articles:
            article_published_at = time.strftime('%Y-%m-%d', time.localtime(article['datetime']))
            if article_published_at == yesterday:
                post_title = article['title']
                update = Post.query.filter_by(title=post_title).first()
                if update:
                    print(post_title + ':已经有这篇文章了')
                    continue
                else:
                    post_url = article['content_url']
                    post_content = get_post_content(get_html(post_url))
                    html_content = post_content[0]
                    text_content = post_content[1]
                    keywords = get_post_keywords(post_title + text_content)
                    published_at = article['datetime']
                    post = Post(
                        title=post_title,
                        url=post_url,
                        text=text_content,
                        html=html_content,
                        keywords=keywords,
                        wx_id=history_info['gzh']['wechat_id'],
                        wx_title=history_info['gzh']['wechat_name'],
                        wx_logo=history_info['gzh']['headimage'],
                        author=article['author'],
                        cover=article['cover'],
                        abstract=article['abstract'],
                        is_marked=0,
                        published_at=published_at
                    )
                db.session.add(post)
                db.session.commit()
                print(post_title + ':保存到数据库了')
        time.sleep(random.randint(1, 10))
    end_time = time.time()
    print('获取数据总耗时：', end_time - start_time)