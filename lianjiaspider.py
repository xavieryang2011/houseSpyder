from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import pandas as pd

class lianjiaspider(object):
	"""docstring for lianjiaspider"""
	def __init__(self, arg):
		super(lianjiaspider, self).__init__()
		self.arg = arg
		self.ua = UserAgent()
		self.headers = {"User-Agent":self.ua.random}
		self.datas = list()

	def getMaxPage(self,url):
		response = requests.get(url,headers=self.headers)
		if response.status_code == 200:
			source = response.text
			soup = BeautifulSoup(source,'html.parser')
			a = soup.find_all("div",class_="page-box house-lst-page-box")
			maxpage = eval(a[0].attrs["page-data"])["totalPage"]
			return maxpage
		else:
			print('请示错误：{0}'.format(response.status_code))
			return None
		pass
	def parsePage(self,url):
		max_page = self.getMaxPage(url)
		for i in range(1,max_page+1):
			url = url+'/pg{}'.format(i)
			print('当前正在抓取第{}页数据地址{}'.format(i,url))
			response = requests.get(url,headers=self.headers)
			soup = BeautifulSoup(response.text,'html.parser')
			a = soup.find_all("div",class_="info-panel")
			for j in range(1,len(a)):
				try:
					link = a[j].find("a")["href"]
					print('明细页url:{0}'.format(link))
					detail=self.parseDetail(link)
					self.datas.append(detail)
					pass
				except:
					print('获取明细url出错')
			pass
		print('所有数据抓取完成，正在写入csv')
		data = pd.DataFrame(self.datas)
		data.to_csv("链家网租房数据.csv",encoding='utf_8_sig')
		pass
	def parseDetail(self,url):
		detail = {}
		response = requests.get(url,headers=self.headers)
		soup = BeautifulSoup(response.text,'html.parser')
		d = soup.find("div",class_="content zf-content")
		detail["月租金"] = d.find("span",class_="total").text.strip()
		detail["面积"] = d.find_all("p",class_="lf")[0].text[3:].strip()
		detail["房屋户型"] = d.find_all("p",class_="lf")[1].text[5:].strip()
		detail["楼层"] = d.find_all("p",class_="lf")[2].text[3:].strip()
		detail["朝向"] = d.find_all("p",class_="lf")[3].text[5:].strip()
		detail["位置"] = d.find_all("p")[6].find("a").text.strip() 
		detail["小区"] = d.find_all("p")[5].find("a").text.strip()
		print(detail)
		return detail
if __name__=='__main__':
	url = "https://bj.lianjia.com/zufang"
	spider = lianjiaspider(url)
	spider.parsePage(url)
