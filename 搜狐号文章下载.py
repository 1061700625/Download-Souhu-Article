# -*- coding: utf-8 -*-

import sys, os
import re
import time
from bs4 import BeautifulSoup
import requests
import json
import urllib.parse
import math

global art_num  # 总文章数


def get_url(xpt):  # 获取URL集合
    url_buf = []  # 存放URL
    datas = []
    pagenumber = 0  # 页数
    for i in range(math.ceil(art_num/10)):
        pagenumber = pagenumber + 1
        print(">> 解析第[%d]页" % pagenumber)
        url_ori = r"https://mp.sohu.com/apiV2/profile/newsListAjax?xpt=" + xpt + "=&pageNumber=" + str(
            pagenumber) + r"&pageSize=10&categoryId="
        try:
            html = requests.get(url_ori).json()
            html_json = json.loads(html)  # 转为json格式
        except Exception as e:
            print(e)
        finally:
            if (html_json["status"] == 1):  # 结束
                print("结束")
                break
            else:
                datas.append(html_json["data"])  # 存信息
                print(datas[pagenumber - 1])
    print("解析完毕\r\n")

    print(">> 分割地址:")
    id = 0
    if (os.path.exists("spider.txt")):  # 如果已经存在
        os.remove("spider.txt")  # 删除该文件
    for i in datas:
        for j in i:
            id = id + 1
            title = urllib.parse.unquote(j["title"])  # utf8转中文显示
            url = "http://" + j["url"].split("//")[1]
            print("[" + str(id) + "] ", title, " ", url)
            url_buf.append("[" + str(id) + "] " + title + " " + url)  # 存入 名称+地址
            with open("spider.txt", 'a+', encoding='utf-8') as fp:
                fp.write("*" * 100 + "\n")
                fp.write("[" + str(id) + "] " + title + " " + url + "\n")  # 写入本地文件
                fp.close()
    print(">> 地址信息已保存到本地")
    return url_buf


def get_content(url_buf):  # 获取地址对应的文章内容
    each_title = ""  # 初始化
    each_url = ""  # 初始化

    splits_num = len(url_buf.split(" "))  # 以空格分割字符串
    if (splits_num > 3):  # 有多余空格，说明标题里含有空格了
        each_title = url_buf.split(" ")[0] + url_buf.split(" ")[-2]  # 拼接标题
    else:
        each_title = url_buf.split(" ")[0] + url_buf.split(" ")[1]  # 拼接标题
    each_title = re.sub(r'[\|\/\<\>\:\*\?\\\"]', "_", each_title)  # 剔除不合法字符

    filepath = rootpath + "/" + each_title  # 为每篇文章创建文件夹
    if (not os.path.exists(filepath)):  # 若不存在，则创建文件夹
        os.makedirs(filepath)
    os.chdir(filepath)  # 切换至文件夹

    each_url = url_buf.split(" ")[-1]  # 获得文章URL
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    }
    html = requests.get(each_url, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')
    article = soup.find(class_="article").find_all("p")  # 查找文章内容位置
    img_urls = soup.find("article").find_all("img")  # 获得文章图片URL集

    print("*" * 60)
    print(each_title)
    print(">> 保存文档 - ", end="")
    for i in article:
        line_content = i.get_text()  # 获取标签内的文本
        # print(line_content)
        if (line_content != None):  # 文本不为空
            with open(each_title + r'.txt', 'a+', encoding='utf-8') as fp:
                fp.write(line_content + "\n")  # 写入本地文件
                fp.close()
    print("完毕!")
    print(">> 保存图片 - %d张" % len(img_urls), end="")
    for i in range(len(img_urls)):
        if (not ("http:" in img_urls[i]["src"])):
            pic_down = requests.get("http:" + img_urls[i]["src"])
        else:
            pic_down = requests.get(img_urls[i]["src"])
        with open(str(i) + r'.jpeg', 'ab+') as fp:
            fp.write(pic_down.content)
            fp.close()
    print("完毕!\r\n")



global rootpath  # 全局变量，存放路径
if __name__ == '__main__':

    # url = "https://www.sohu.com/a/290059377_479499?sec=wd"
    # html = requests.get(url)
    # soup = BeautifulSoup(html.text, 'lxml')
    # img = soup.find("article").find_all("img")
    # print(img)
    # print(img[0]["src"])

    url = input("输入地址,（不输入则默认为机甲同盟个人主页）：")
    if (url == ""):
        url = "https://mp.sohu.com/profile?xpt=b1NlSFRzMGJ5Sl84dnh2ZllseHMyMGxsejFVSUB3ZWNoYXQuc29odS5jb20="
    # url = r'https://mp.sohu.com/profile?xpt=N0RCRERGRTA3MTdDOUM4QjFGM0QwRTc4Q0RDMUFGQ0RAcXEuc29odS5jb20='
    xpt = url.split("=")[1]

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')
    name = soup.find(class_="author-name").get_text().strip()  # 查找搜狐号
    art_num = int(soup.find(class_="art_num").get_text().strip())  # 查找文章数

    print("*" * 60)
    print("URL => ", url)
    print("搜狐号 => ", name)
    print("文章数 => ", art_num)
    print("*" * 60)
    print("\r\n")

    rootpath = os.getcwd() + r"/spider/" + name
    if (not os.path.exists(rootpath)):  # 若不存在，则创建文件夹
        os.makedirs(rootpath)
    os.chdir(rootpath)  # 切换至文件夹

    url_buf = get_url(xpt)
    for i in url_buf:
        get_content(i)
    print("\r\n>> 程序结束!<<")


