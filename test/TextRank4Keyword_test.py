#-*- encoding:utf-8 -*-
from __future__ import print_function

import sys
import time
import urllib2
from bs4 import BeautifulSoup

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs
from textrank4zh import TextRank4Keyword

# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]

def getPartText(partUrl):
    url = "https://m.qidian.com" + partUrl
    res = ""
    try:
        req = urllib2.Request(url, headers=hds[0])
        source_code = urllib2.urlopen(req, data=None, timeout=10).read()
        plain_text = str(source_code).strip()
        soup = BeautifulSoup(plain_text)
        soupAllBooksPerPage = soup.find('section', attrs={'class': 'read-section jsChapterWrapper'})
        res = str(soupAllBooksPerPage.text)
        res = res.replace(" ","")
    except Exception, e:
        print("getPartText error:", e)
    return res


def getCharactor(bookUrl):
    res = ""
    bookId = bookUrl.replace("https://book.qidian.com/info/", "")
    url = "https://m.qidian.com/book/" + bookId + "/catalog"
    try:
        #time.sleep(0.5)
        req = urllib2.Request(url, headers=hds[0])
        source_code = urllib2.urlopen(req, data=None, timeout=10).read()
        plain_text = str(source_code).strip()
        soup = BeautifulSoup(plain_text)
        soupAllBooksPerPage = soup.find_all('li', attrs={'class': 'chapter-li jsChapter'})

        # 爬取前10章的内容
        for i in range(min(20, len(soupAllBooksPerPage))):
            titlePart = soupAllBooksPerPage[i]
            partUrl = titlePart.a.attrs['href']
            partText = getPartText(partUrl)
            res += partText
    except Exception, e:
        print("getCharactor error:", e)
    return res


tr4w = TextRank4Keyword()

# 从1开始
def getKeywordForFile(fileIndex):
    global  doneMap
    doneMap[fileIndex] = False
    pathBase = "/home/work/zhaoze/project/book/qidianBook/外部流行小说/起点小说名单/"
    pathSaveBase = "/home/work/zhaoze/project/book/qidianBook/外部流行小说/起点new/"
    # pathBase = "/home/zhaoze/my-work/book_optimize/外部流行小说/起点小说名单/"
    # pathSaveBase = "/home/zhaoze/my-work/book_optimize/外部流行小说/起点new/"
    i = fileIndex
    path = pathBase + "res_page" + str(i) + ".txt"
    pathSave = pathSaveBase + "res_page" + str(i) + ".txt"
    fw = open(pathSave, "w")
    fw.truncate()
    count = 0
    for line in open(path).readlines():
        msg = line.strip().split("\t")
        url = msg[1]
        text = getCharactor(url)
        if(text == ""):
            text = getCharactor(url)
        res = line.strip()
        res += "\t" + text
        # tr4w.analyze(text=text,lower=True, window=3, pagerank_config={'alpha':0.85})
        # for item in tr4w.get_keywords(4, word_min_len=2):
        #     res += "\t" + item.word
        #     #print(item.word, item.weight, type(item.word))
        fw.write(res+"\n")
        count += 1
        print("文件",i+1, "完成", count)
    fw.close()
    print("完成文件", i+1)
    doneMap[fileIndex] = True

def getKeyword():
    pathBase = "/home/zhaoze/my-work/book_optimize/外部流行小说/起点小说名单/"
    pathSaveBase = "/home/zhaoze/my-work/book_optimize/外部流行小说/起点new/"

    for i in range(52):
        path = pathBase + "res_page" + str(i+1) + ".txt"
        pathSave = pathSaveBase + "res_page" + str(i+1) + ".txt"
        fw = open(pathSave, "w")
        fw.truncate()
        count = 0
        for line in open(path).readlines():
            msg = line.strip().split("\t")
            url = msg[1]
            text = getCharactor(url)
            tr4w.analyze(text=text,lower=True, window=3, pagerank_config={'alpha':0.85})
            res = line.strip()
            for item in tr4w.get_keywords(4, word_min_len=2):
                res += "\t" + item.word
                #print(item.word, item.weight, type(item.word))
            fw.write(res+"\n")
            count += 1
            print("文件",i+1, "完成", count)
        fw.close()
        print("完成文件", i+1)


# print('--phrase--')
#
# for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num = 0):
#     print(phrase, type(phrase))

import thread
import time


# 设置线程完成标志
doneMap = {}
for i in range(52):
    doneMap[i+1] = False


def multiAnalysis():
    try:
        for i in range(52):
            thread.start_new_thread(getKeywordForFile, (i+1,))
            time.sleep(0.5)
    except:
        print("Error: unable to start thread")

    runing = True
    while runing:
        runing = False
        for i in doneMap:
            if(not doneMap[i]):
                runing = True
                break
            else:
                print("part",i,"done")

if __name__ == '__main__':
    multiAnalysis()
    # text = "第一章大漠中的彼岸花。 大漠孤烟直，长河落日圆。"
    # tr4w.analyze(text=text,lower=True, window=3, pagerank_config={'alpha':0.85})
    # for item in tr4w.get_keywords(4, word_min_len=2):
    #     print(item.word, item.weight, type(item.word))
    # print("主函数返回")
