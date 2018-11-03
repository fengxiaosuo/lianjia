#!/usr/bin/python
#coding=utf-8

import sys
import pycurl
import re
import StringIO
import urllib
import random

# get html from url
def get_html(url):
	b=StringIO.StringIO() 
	c=pycurl.Curl() 
	c.setopt(pycurl.URL, url) 
	c.setopt(pycurl.HTTPHEADER, ["Accept:"]) 
	c.setopt(pycurl.WRITEFUNCTION, b.write) 
	c.setopt(pycurl.FOLLOWLOCATION, 1) 
	c.setopt(pycurl.MAXREDIRS, 5) #指定HTTP重定向的最大数
	c.perform() 

	# check if we are OK
	if(c.getinfo(c.HTTP_CODE) == 200):
		html = b.getvalue()
	else:
		print "ERR: get_html failed. http code:" + str(c.getinfo(c.HTTP_CODE))
		html = ""
	b.close()
	c.close()
	return html

# get image url list in given html string
def get_image_list(html):
	# define a 正则表达式 for all jpg urls
    #reg=r'src="(.*?\.jpg)"'
	reg=r'"pageNum":[0-9]*?,            "objURL":"(http://.{5,150}\.(jpg|png|jpeg))"'

	patt = re.compile(reg)
	image_list = re.findall(patt,html)
	#print image_list

	print "INF: below are all jpg or png links inside given html\n"
	for imgurl in image_list:
		print "  "+imgurl[0]
	print "INF: end of list\n"
	
	return image_list

def save_images(list, picture_path, image_count=3):
	x = 0
	local_img_list = []
	for imgurl in list:
		print "INF: save_images "+str(image_count)+" from:" + imgurl[0]
		try:
			pic_file_path = picture_path+target+"_"+str(x)+".jpg"
			print "INF: save_images at:" + pic_file_path
			pic_file = open(pic_file_path, "w+")
			img = get_html(imgurl[0]) # get_html can also get img
			if(img != ""):
				print "INF: save_images img is not empty"
				pic_file.write(img)
				local_img_list.append(pic_file_path)
			else:
				print "ERR: save image "+str(x)+" failed from url "+imgurl[0]
				pic_file.close()
				continue
		except:
			print "ERR: save image "+str(x)+" failed!"
			continue
		else:
			print "INF: save image "+str(x)+" succeed!"
			pass
		x=x+1
		if (int(x)>=int(image_count)):
			break

	return local_img_list

def get_house_list(html):
	# define a re
    #reg=r'src="(.*?\.jpg)"'
	reg=r'<a class="img " href="(https://bj\.lianjia\.com/ershoufang/[0-9]+\.html)"'

	patt = re.compile(reg)
	house_list = re.findall(patt,html)
	#print house_list

	'''
	print "INF: below are all house urls inside given html\n"
	for house_url in house_list:
		print "  "+house_url
		pass
	print "INF: end of list\n"
	'''
	
	return house_list

def get_list(html, patt=""):
	# define a re
	#<a href="/ershoufang/xicheng/"  title="北京西城在售二手房 ">西城</a>
	reg=r'<a href="/ershoufang/(.*?)/"  title="北京.{2,10}在售二手房 ">.{2,10}</a>'

	# find patt from html into list
	patt = re.compile(reg)
	list = re.findall(patt,html)

	'''
	print "INF: below are all members in list\n"
	for member in list:
		print "  "+member
		pass
	print "INF: end of list\n"
	'''
	
	return list

def get_sub_list(html, patt=""):
	# define a re
	#<a href="/ershoufang/andingmen/" >安定门</a>
	reg=r'<a href="/ershoufang/(.*?)/" >.{2,30}</a>'

	# find patt from html into list
	patt = re.compile(reg)
	list = re.findall(patt,html)

	'''
	print "INF: below are all members in list\n"
	for member in list:
		print "  "+member
		pass
	print "INF: end of list\n"
	'''
	
	return list
	
def get_house_info(url, csv_file):
	html = get_html(url)
	if html == "":
		print "ERR: html get failed!"
		return

	# 房源编号,小区,小区链接,价格,户型图,房屋户型,所在楼层,建筑面积,房屋朝向,装修情况,梯户比例,供暖方式,配备电梯,产权年限,挂牌时间,交易权属,上次交易,房屋用途,房屋年限,产权所属
	# 房源编号
	patt = re.compile(r'https://bj.lianjia.com/ershoufang/([0-9]*?).html')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",,")

	# 小区,小区链接
	patt = re.compile(r'<a href="(/xiaoqu/[0-9]*?/)" target="_blank" class="info ">(.*?)</a>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(2)+","+"https://bj.lianjia.com/"+result.group(1)+",")
	else:
		csv_file.write(",,")

	# 价格
	patt = re.compile(r'<span class="total">([0-9|\.]*?)</span><span class="unit"><span>(.*?)</span></span>')
	price = re.search(patt,html)
	if price:
		csv_file.write(price.group(1) + price.group(2)+",")
	else:
		csv_file.write(",")

	# 户型图
	patt = re.compile(r'<img src="(https://.{5,150}\.jpg)" alt="户型图">')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 房屋户型
	#<li><span class="label">房屋户型</span>51.4㎡</li>
	patt = re.compile(r'<li><span class="label">房屋户型</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 所在楼层
	patt = re.compile(r'<li><span class="label">所在楼层</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 建筑面积
	patt = re.compile(r'<li><span class="label">建筑面积</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 房屋朝向
	patt = re.compile(r'<li><span class="label">房屋朝向</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 装修情况
	patt = re.compile(r'<li><span class="label">装修情况</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 梯户比例
	patt = re.compile(r'<li><span class="label">梯户比例</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 供暖方式
	patt = re.compile(r'<li><span class="label">供暖方式</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 配备电梯
	patt = re.compile(r'<li><span class="label">配备电梯</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 产权年限
	patt = re.compile(r'<li><span class="label">产权年限</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 挂牌时间
	patt = re.compile(r'<li><span class="label">挂牌时间</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	#交易权属
	patt = re.compile(r'<li><span class="label">交易权属</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 上次交易
	patt = re.compile(r'<li><span class="label">上次交易</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 房屋用途
	patt = re.compile(r'<li><span class="label">房屋用途</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 房屋年限
	patt = re.compile(r'<li><span class="label">房屋年限</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")

	# 产权所属
	patt = re.compile(r'<li><span class="label">产权所属</span>(.*?)</li>')
	result = re.search(patt,html)
	if result:
		csv_file.write(result.group(1)+",")
	else:
		csv_file.write(",")
	
	csv_file.write("\n")
	return

###########################################################################
#
# main function start here
#
###########################################################################

# 准备工作
all_bj_house_list = []
html_file = open("all_bj_house_list.txt", "w+")
csv_file = open("bj_house.csv", "w+")
csv_file.write("房源编号,小区,小区链接,价格,户型图,房屋户型,所在楼层,建筑面积,房屋朝向,装修情况,梯户比例,供暖方式,配备电梯,产权年限,挂牌时间,交易权属,上次交易,房屋用途,房屋年限,产权所属\n")

# 获取链家网站北京所有区的链接，存入list
url = "https://bj.lianjia.com/ershoufang/"
html = get_html(url)
dist_list = []
if html != "":
	dist_list = get_list(html)
	if len(dist_list)==0:
		print "ERR: dist_list is empty!"
		exit(0)
else:
	print "ERR: html get failed!"
	exit(0)

# 链家网站最多显示100页，每页30个房源。一个区可能超过3000个房源，因此需要获取区里所有的片区
subdist_list = []
for member in dist_list:
	print "INF: Getting sub dist from district " + member
	url2 = "https://bj.lianjia.com/ershoufang/"+member
	html = get_html(url2)
	if html != "":
		this_dist_list = get_sub_list(html)
		if len(this_dist_list)==0:
			print "ERR: subdist list of "+member+" is empty!"
			continue
		else:
			subdist_list.extend(this_dist_list)
	else:
		print "ERR: html get failed!"
		continue

# 从每个片区里获取所有的房源并保存
for subdist in subdist_list:
	print subdist
	url3 = "https://bj.lianjia.com/ershoufang/"+str(subdist)
	print "INF: Loading sub dist " + url3
	page_num = 1
	
	# 获取本片区的房源页数
	html = get_html(url3)
	if html == "":
		print "ERR: html get failed!"
		continue
	#data='{"totalPage":37,"curPage":1}'
	reg=r'data=\'{"totalPage":([0-9]*?),"curPage":.}\''
	patt = re.compile(reg)
	pagecount = re.search(patt,html)
	if pagecount:
		print "INF: page count is "+pagecount.group(1)
	else:
		print "ERR: can't find anything in this page!"
		continue
	
	# 获取每页中的房源，一般是30个
	while(page_num <= int(pagecount.group(1))):
	#while(page_num <= 3):
		url4 = url3+"/pg"+str(page_num)+"/"
		print "INF: Loading page " + url4

		html = get_html(url4)
		if html != "":
			# 把页面中的房源链家读到房源list中
			house_list = get_house_list(html)

			if len(house_list)>0:
				for house_url in house_list:
					# 写房源链接文件
					html_file.write(house_url+"\n")
					# 写房源详情文件
					get_house_info(house_url, csv_file)
				# 把房源存入所有房源列表
				#all_bj_house_list.extend(house_list)
				print "INF: "+str(len(house_list))+" house urls loaded!"
			else:
				print "ERR: house_list is empty!"
		else:
			print "ERR: html get failed!"
			break

		page_num = page_num+1


'''
# 如果需要可以把所有房源链接的list打出来
print "INF: below are all house urls we get in all_bj_house_list\n"
for house_url in all_bj_house_list:
	print "  "+house_url
	pass
print "INF: end of list\n"
'''

html_file.close()
csv_file.close()

print "INF: end of function"
