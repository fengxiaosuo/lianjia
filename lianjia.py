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

###########################################################################
#
# main function start here
#
###########################################################################

# get html contains images from Baidu Baike
all_bj_house_list = []
html_file = open("all_bj_house_list.txt", "w+")

# get distrit list
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

for member in dist_list:
	# general dist url
	url2 = "https://bj.lianjia.com/ershoufang/"+member
	print "INF: Loading " + url2
	
	page_num = 1
	
	# get page count
	html = get_html(url2)
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
	
	while(page_num <= int(pagecount.group(1))):
		# generate page url
		url3 = url2+"/pg"+str(page_num)+"/"
		print "INF: Loading " + url3

		# save the result into html object
		html = get_html(url3)
		if html != "":
			house_list = get_house_list(html)

			if len(house_list)>0:
				for house_url in house_list:
					html_file.write(house_url+"\n")
				all_bj_house_list.extend(house_list)
				print "INF: "+str(len(house_list))+" house urls loaded!"
			else:
				print "ERR: house_list is empty!"
		else:
			print "ERR: html get failed!"
			break

		page_num = page_num+1


'''
print "INF: below are all house urls we get in all_bj_house_list\n"
for house_url in all_bj_house_list:
	print "  "+house_url
	pass
print "INF: end of list\n"
'''



html_file.close()

print "INF: end of function"
