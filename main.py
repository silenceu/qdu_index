# coding=utf-8
# python3

import os  # 系统调用模块，本例中主要用于文件夹相关的操作
import re  # 正则表达式模块 用于校验url地址的合法性
import csv  # 主要用来创建并存储csv文件
import chardet  # 检验html网页的编码类型
import socket
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup  # 解析


def get_content_by_url(url):
    """
    根据url获取整个网页的所有的内容
    :param url:
    :return:
    """
    try:
        if re.match('^[a-giz].*\.html*', url):
            url = 'http://www.qdu.edu.cn/' + url
        html = urlopen(url, timeout=30)
    except urllib.request.HTTPError as e:
        print(url, e.msg)
        return None
    except UnicodeEncodeError:
        print('EncodeError  :', url)
        return None
    except socket.timeout:
        print('Time Out  :', url)
        return None
    except Exception as e:
        print('Some Error! Skip!')
        return None
    else:
        return html


def save_html(url, root_path, child_path):
    """
    根据新闻所属版块保存html文件到对应的文件夹
    :param url:
    :param root_path:
    :param child_path:
    :return:
    """
    html = get_content_by_url(url)
    if html is None:
        return
    dir_path = root_path + child_path[0]
    file_path = dir_path + child_path[1]
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    with open(file_path, 'wb') as f:
        f.write(html.read())


def generate_index(newsid, url):
    """
    提取网页中的关键信息：新闻标题、编码、网址
    :param newsid:
    :param url:
    :return:
    """
    html = get_content_by_url(url)
    if html is None:
        return
    bfobj = BeautifulSoup(html.read(), 'html.parser')
    try:
        if bfobj.head.title:
            title = bfobj.head.title.get_text()
        info = chardet.detect(get_content_by_url(url).read())
        if info is not None:
            charset = info['encoding']
        else:
            charset = 'None'
        meta = bfobj.find('meta', {'name': 'keywords'})
        if meta is None:
            keyword = 'None'
        else:
            keyword = meta['content']
    except AttributeError:
        print('AttributeError', url)
        pass
    except TypeError:
        print('Type Error', url)
        pass
    print(title, charset, keyword)
    return (newsid, title, charset, url, keyword)


if __name__ == '__main__':
    socket.setdefaulttimeout(10)
    url = 'http://www.qdu.edu.cn'
    root_path = 'qduwebsite'
    child_paths = (['', '/index.htm'],
                   [u'/青大要闻', '/qdyw.htm'],
                   [u'/文化学术', '/whxs.htm'],
                   [u'/媒体青大', '/mtqd.htm'],
                   [u'/通知公告', '/tzgg.htm'])
    newsid = 1
    index = list()

    for idx, child_path in enumerate(child_paths):
        save_html(url + child_path[1], root_path, child_path)
        html = get_content_by_url(url + child_path[1])
        index.append(generate_index(newsid, url + child_path[1]))
        newsid += 1
        bfobj = BeautifulSoup(html.read(), "html.parser")
        a_tags = bfobj.find_all('a', {'class': 'c52102'})
        for a in a_tags:
            href = a['href']
            child_child_path = [child_path[0], href[href.rfind('/'):href.rfind('.')] + '.html']
            save_html(a['href'], root_path, child_child_path)
            index.append(generate_index(newsid, a['href']))
            newsid += 1
    while None in index:
        index.remove(None)
    headers = ['ID', 'Title', 'charset', 'URL', 'Keywords']
    with open(root_path + '/index.csv', 'w', encoding='utf-8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(index)
