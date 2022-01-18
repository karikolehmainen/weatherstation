#https://api.nasa.gov/DONKI/CME?startDate=2022-01-05&endDate=2022-01-05&api_key=01TjRKAF5JKRERBIKdYxI7DnQvJNARvjfh7gMiId
from time import sleep
from datetime import datetime
from datetime import timedelta
import json
import requests
from html.parser import HTMLParser
from urllib.request import urlretrieve

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
	def clean(self):
		self.data = ""
		self.image_den = ""
		self.image_vel = ""

class NASA_DONKI_CME:
	api_key = "01TjRKAF5JKRERBIKdYxI7DnQvJNARvjfh7gMiId"

	def __init__(self):
		# init some stuff
		self.url = "https://api.nasa.gov/DONKI/CME"
		self.htmlParser = MyHTMLParser()

	def getEventList(self):
		# response = requests.get("http://api.open-notify.org/astros.jkson")
		today = datetime.utcnow().date()
		yesterday = today - timedelta(days=1)

		print("from: "+str(yesterday)+" to: "+str(today))
		response = requests.get(self.url+"?startDate="+str(yesterday)+"&endDate="+str(today)+"&api_key="+self.api_key)
		data = response.json()
		print("events: "+str(len(data)))
		link = ""
		for event in data:
			self.event_id = event["activityID"]
			print("\n"+self.event_id)
			analysis = event["cmeAnalyses"]
			print(event)
			enlilList = analysis[0]["enlilList"]
			if (enlilList != None):
				print(enlilList)
				for enlil in enlilList:
					arrivaltime = enlil["estimatedShockArrivalTime"]
					link = enlil["link"]
		print("\n"+self.event_id)
		if (link != ""):
			self.getNotification(link, self.event_id)
		else:
			print("getEventList link is null: "+ self.event_id)

	def getNotification(self, url, id):
		print("getNotification: "+ url)
		response = requests.get(url)
		#print(response.text)
		self.htmlParser.feed(response.text)
		#print(self.htmlParser.data)
		self.publishCMEEvent(self.htmlParser.data, self.event_id)

	def publishCMEEvent(self, body, title):
		post_url = "http://localhost/index.php/wp-json/wp/v2/posts"
		query = "?search="+title
		response = requests.get(post_url+query)
		if (len(response.json())>0):
			print(response.json())
			self.htmlParser.clean()
			return
		dataset = {"title":title,"content":body,"status": "publish","excerpt":"Solar CME Event", "categories": [4]}
		#dataset = {"author": "abyssuser","title":title,"content":body,"status": "publish","excerpt":"Solar CME Event"}
		print(dataset)
		data = json.dumps(dataset)
		headers = {"Authorization": "Basic"}
		auth = ('abyssuser','3mZ9Bqff0g6^1pBwt3')
		#response = requests.post(post_url,data,headers=headers,auth=auth)
		response = requests.post(post_url,dataset,auth=auth)
		print(response.content)
		urlretrieve(self.htmlParser.image_vel, "/var/www/html/sol_velocity.gif")
		urlretrieve(self.htmlParser.image_den, "/var/www/html/sol_density.gif")
		#self.uploadImage("sol_velocity.gif", "/var/www/html/sol_velocity.gif")
		#self.uploadImage("sol_density.gif", "/var/www/html/sol_density.gif")
		self.htmlParser.clean()

	def uploadImage(self, name, path):
		mediaImageBytes = open(path, 'rb').read()
		print("uploadImage: " + name)
		curHeaders = {
			"Content-Type": "image/gif",
			"Accept": "application/json",
			'Content-Disposition': "attachment; filename=%s" % name,
		}
		auth = ('abyssuser','3mZ9Bqff0g6^1pBwt3')

		resp = requests.post(
			"https://www.crifan.com/wp-json/wp/v2/media/133",
			headers=curHeaders,
			data=mediaBytes,
			auth=auth
		)


sw = NASA_DONKI_CME()
while(1):
	sw.getEventList()
	# check events every 30 mins
	sleep(1800)

