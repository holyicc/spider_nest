# coding:utf-8
import re
import jieba  # 分词包
import numpy  # numpy计算包
import pandas as pd
from urllib import request
from bs4 import BeautifulSoup as bs

resp = request.urlopen('https://movie.douban.com/nowplaying/hangzhou/')
html_data = resp.read().decode('utf-8')
# print(html_data)

soup = bs(html_data, 'html.parser')
nowplaying_movie = soup.find_all('div', id='nowplaying')
nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
# print(nowplaying_movie_list[0])

nowplaying_list = []
for item in nowplaying_movie_list:
    nowplaying_dict = {}
    nowplaying_dict['id'] = item['data-subject']
    for tag_img_item in item.find_all('img'):
        nowplaying_dict['name'] = tag_img_item['alt']
        nowplaying_list.append(nowplaying_dict)

# print(nowplaying_list)

requrl = 'https://movie.douban.com/subject/' + nowplaying_list[0]['id'] + '/comments' + '?' + 'start=0' + '&limit=20'
resp = request.urlopen(requrl)
html_data = resp.read().decode('utf-8')
soup = bs(html_data, 'html.parser')
comment_div_list = soup.findAll('div', class_='comment')

comment_list = []

for item in comment_div_list:
    if item.find_all('p')[0].string is not None:
        comment_list.append(item.find_all('p')[0].string)
# print(comment_list)

comments_collection = ''
for comment in range(len(comment_list)):
    comments_collection = comments_collection + (str(comment_list[comment]).strip())
# print(comments_collection)

# 通过re模块使用正则表达式
pattern = re.compile(r'[\u4e00-\u9fa5]+')
filter_data = re.findall(pattern, comments_collection)
cleaned_comments = ''.join(filter_data)
# print(cleaned_comments)

# 使用结巴分词 引入jieba ，又因为结巴需要使用pandas，so～

segment = jieba._lcut(cleaned_comments)
words_framed = pd.DataFrame({'segment': segment})

# 查看分词结果
# words_framed.head()
# with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
#     print(words_framed)

# 数据与停用词比对，筛掉无意义的高频词
stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],
                        encoding='utf-8')  # quoting=3全不引用
words_df = words_framed[~words_framed.segment.isin(stopwords.stopword)]

# 词频统计
words_stat = words_framed.groupby(by=['segment'])['segment'].agg({"计数": numpy.size})
words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

# 查看分词结果
words_stat.head()
with pd.option_context('display.max_rows', None, 'display.max_columns', 4):
    print(words_stat)
