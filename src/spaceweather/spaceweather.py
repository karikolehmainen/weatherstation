#https://api.nasa.gov/DONKI/CME?startDate=2022-01-05&endDate=2022-01-05&api_key=01TjRKAF5JKRERBIKdYxI7DnQvJNARvjfh7gMiId
from time import sleep
from datetime import datetime
from datetime import timedelta
import json
import requests
from html.parser import HTMLParser
from urllib.request import urlretrieve

WP_URL = "http://localhost/index.php/wp-json/wp/v2/posts"
WP_USER = "foo"
WP_PASS = "bar"
WP_CAT = 1
API_KEY = ""

class MyHTMLParser(HTMLParser):
	message = False
	content = False
	image_den = ""
	image_vel = ""
	data = ""

	def handle_starttag(self, tag, attrs):
		if(self.message):
			if (tag == "table"):
				self.content = True
		if(self.content):
			#print("Encountered a start tag:", tag)
			#print("Encountered a start tag:", attrs)
			if (tag != "table" and tag != "tr" and tag != "td"):
				self.data += "<"+tag
				if (len(attrs)>0):
					self.data += " "+str(attrs[0][0])
					self.data += "=\""+str(attrs[0][1])+"\""
				self.data += ">"


	def handle_endtag(self, tag):
		if(self.message):
			if (tag == "body"):
				self.message = False
				self.content = False
		if(self.content):
			#print("Encountered an end tag :", tag)
			if (tag != "table" and tag != "tr" and tag != "td"):
				self.data += "</"+tag+">"

	def handle_data(self, data):
		if (data.strip() == "View SW Activity"):
			self.message = True
		if(self.content and len(data.strip()) > 1):
			if ("Inner Planets Link" in data):
				self.content = False
			else:
			#print("Encountered some data  :", data)
				self.data += data
		if (".tim-den.gif" in data):
			self.image_den = data
			self.data += "<img src=\""+data+"\"><br>"
		if (".tim-vel.gif" in data):
			self.image_vel = data

			self.data += "<img src=\""+data+"\"><br>"

class NASA_DONKI_CME:
	api_key= API_KEY

	def __init__(self):
		# init some stuff
		self.url = "https://api.nasa.gov/DONKI/CME"
		self.htmlParser = MyHTMLParser()

	def getEventList(self):
		today = datetime.utcnow().date()
		yesterday = today - timedelta(days=1)

		print("from: "+str(yesterday)+" to: "+str(today))
		response = requests.get(self.url+"?startDate="+str(yesterday)+"&endDate="+str(today)+"&api_key="+self.api_key)
		data = response.json()
		print("events: "+str(len(data)))
		link = ""
		for event in data:
			self.event_id = event["activityID"]
			analysis = event["cmeAnalyses"]
			enlilList = analysis[0]["enlilList"]
			if (enlilList != None):
				print(enlilList)
				for enlil in enlilList:
					arrivaltime = enlil["estimatedShockArrivalTime"]
					link = enlil["link"]
		print("\n"+self.event_id)
		print(link)
		self.getNotification(link, self.event_id)

	def getNotification(self, url, id):
		response = requests.get(url)
		self.htmlParser.feed(response.text)
		self.publishCMEEvent(self.htmlParser.data, self.event_id)

	def publishCMEEvent(self, body, title):
		post_url = WP_URL
		query = "?search="+title
		response = requests.get(post_url+query)
		if (len(response.json())>0):
			print(response.json())
			return
		dataset = {"title":title,"content":body,"status": "publish","excerpt":"Solar CME Event", "categories": [WP_CAT]}
		#print(dataset)
		data = json.dumps(dataset)
		headers = {"Authorization": "Basic"}
		auth = (WP_USER,WP_PASS)
		response = requests.post(post_url,dataset,auth=auth)
		#print(response.content)
		urlretrieve(self.htmlParser.image_vel, "/var/www/html/sol_velocity.gif")
		urlretrieve(self.htmlParser.image_den, "/var/www/html/sol_density.gif")

sw = NASA_DONKI_CME()
while(1):
	sw.getEventList()
	# check events every 30 mins
	sleep(1800)

