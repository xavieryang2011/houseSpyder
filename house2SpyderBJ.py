import requests
from bs4 import BeautifulSoup
from os import path
from wordcloud import WordCloud, ImageColorGenerator
import jieba.analyse
import matplotlib.pyplot as plt
from scipy.misc import imread
import time
from pymongo import MongoClient



class HouseSpider:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.zfdb = self.client.esfdb
        self.zfdb.authenticate("admin", "123456")

    session = requests.Session()
    baseUrl = "http://esf.fang.com"

    urlDir = {
        "不限": "/house/",
        "朝阳": "/house-a01/",
        "海淀": "/house-a00/",
        "丰台": "/house-a06/",
        "东城": "/house-a02/",
        "西城": "/house-a03/",
        "石景山": "/house-a07/",
        "昌平": "/house-a012/",
        "大兴": "/house-a0585/",
        "通州": "/house-a010/",
        "顺义": "/house-a011/",
        "房山": "/house-a08/",
        "密云": "/house-a013/",
        "门头沟":"/house-a09/",
        "怀柔":"/house-a014/",
        "延庆":"/house-a015/",
        "平谷":"/house-a016/",
        "燕郊":"/house-a0987/",
        "北京周边": "/house-a011817/",#香河，大厂，固安等
    }
    region = "不限"
    page = 100
    # 通过名字获取 url 地址
    def getRegionUrl(self, name="朝阳", page=10):
        urlList = []
        for index in range(page):
            if index == 0:
                urlList.append(self.baseUrl + self.urlDir[name])
            else:
                urlList.append(self.baseUrl + self.urlDir[name] + "i3" + str(index + 1) + "/")

        return urlList


    # MongoDB 存储数据结构
    def getRentMsg(self, title, rooms, area, price,sumprice, address, traffic, region, direction):
        return {
            "title": title,  # 标题
            "rooms": rooms,  # 房间数
            "area": area,  # 平方数
            "price": price,  # 价格
            "sumprice": sumprice, # 总价
            "address": address,  # 地址
            "traffic": traffic,  # 交通描述
            "region": region,  # 区、（福田区、南山区）
            "direction": direction,  # 房子朝向（朝南、朝南北）
        }

    # 获取数据库 collection
    def getCollection(self, name):
        zfdb = self.zfdb
        if name == "不限":
            return zfdb.esf_bj
        if name == "朝阳":
            return zfdb.cy_bj
        if name == "海淀":
            return zfdb.hd_bj
        if name == "丰台":
            return zfdb.ft_bj
        if name == "东城":
            return zfdb.dc_bj
        if name == "西城":
            return zfdb.xc_bj
        if name == "石景山":
            return zfdb.sjs_bj
        if name == "昌平":
            return zfdb.cp_bj
        if name == "通州":
            return zfdb.tz_bj
        if name == "顺义":
            return zfdb.sy_bj
        if name == "大兴":
            return zfdb.dx_bj
        if name == "房山":
            return zfdb.fs_bj
        if name == "门头沟":
            return zfdb.mtg_bj
        if name == "密云":
            return zfdb.my_bj
        if name == "延庆":
            return zfdb.yq_bj
        if name == "怀柔":
            return zfdb.hr_bj
        if name == "平谷":
            return zfdb.pg_bj
        if name == "燕郊":
            return zfdb.yj_bj


    def getOnePageData(self, pageUrl, reginon="不限"):
        rent = self.getCollection(self.region)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'})
        res = self.session.get(
            pageUrl
        )
        soup = BeautifulSoup(res.text, "html.parser")
        if len(pageUrl.split("/"))<6:
           divs = soup.find_all("dd", attrs={"class": "info rel floatr"})  # 获取需要爬取得 div
           for div in divs:
            ps = div.find_all("p")
            try:  # 捕获异常，因为页面中有些数据没有被填写完整，或者被插入了一条广告，则会没有相应的标签，所以会报错
                for index,p in enumerate(ps):  # 从源码中可以看出，每一条 p 标签都有我们想要的信息，故在此遍历 p 标签，
                    text = p.text.strip()
                    # print(text)  # 输出看看是否为我们想要的信息
                    # print("===================================")
                # 爬取并存进 MongoDB 数据库
                roomMsg = ps[1].text.split("|")

                # rentMsg 这样处理是因为有些信息未填写完整，导致对象报空
                area = ps[4].text.strip()[:len(ps[4].text.strip()) - 2]
                rentMsg = self.getRentMsg(
                    ps[0].text.strip(),
                    roomMsg[0].strip(),
                    int(float(area)),
                    int(ps[len(ps) - 1].text.strip()[:len(ps[len(ps) - 1].text.strip()) - 4]),
                    0,
                    ps[2].text.split("\n")[2],
                    ps[3].text.strip(),
                    ps[2].text.split("\n")[1],
                    roomMsg[2].strip(),
                )
                rent.insert(rentMsg)
            except:
                continue
        else:
            divs = soup.find_all("dl", attrs={"class": "clearfix"})  # 获取需要爬取得 div
            # print(divs[0])
            for div in divs:
                ps = div.find_all("p")
                ds=div.find_all("dd")
                try:  # 捕获异常，因为页面中有些数据没有被填写完整，或者被插入了一条广告，则会没有相应的标签，所以会报错
                    for index,p in enumerate(ps):  # 从源码中可以看出，每一条 p 标签都有我们想要的信息，故在此遍历 p 标签，
                        text = p.text.strip()
                        # print(text)  # 输出看看是否为我们想要的信息
                        # print("===================================")
                    # 爬取并存进 MongoDB 数据库
                    roomMsg = ps[1].text.split("|")
                    rooms = ps[1].text.split("\n")[1].strip()
                    direction = ps[1].text.split("\n")[2].strip().split("|")[3]
                    # print(ps[3])
                    # rentMsg 这样处理是因为有些信息未填写完整，导致对象报空
                    area=ps[1].text.split("\n")[2].strip().split("|")[1].strip()[:len(ps[1].text.split("\n")[2].strip().split("|")[1].strip())-2]
                    # print(ps[1].text.split("\n")[2].strip().split("|")[1][:len(ps[1].text.split("\n")[2].strip().split("|")[1])-2])
                    price = ds[1].text.strip().split("\n")[1][:len(ds[1].text.strip().split("\n")[1]) - 4]
                    sumprice=ds[1].text.strip().split("\n")[0][:len(ds[1].text.strip().split("\n")[0])-1]
                    rentMsg = self.getRentMsg(
                        "",
                        rooms,
                        int(float(area)),
                        int(price),
                        int(sumprice),
                        ps[2].text.split("\n")[4].strip(),
                        "",
                        ps[2].text.split("\n")[2].strip(),
                        direction,
                    )
                    rent.insert(rentMsg)
                except :
                    continue


    def setRegion(self, region):
        self.region = region

    def setPage(self, page):
        self.page = page

    def startSpicder(self):
        for url in self.getRegionUrl(self.region, self.page):
            self.getOnePageData(url, self.region)
            print("=================== one page 分割线 ===========================")
            print("=================== one page 分割线 ===========================")
            print("=================== one page 分割线 ===========================")
            time.sleep(5)


spider = HouseSpider()
spider.setPage(11)# 设置爬取页数
spider.setRegion("燕郊")# 设置爬取区域
spider.startSpicder()# 开启爬虫
